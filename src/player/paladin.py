'''
    Avolotion
    Copyright (C) 2014  Grzegorz 'Wezu' Kalinski grzechotnik1984@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
from panda3d.core import *
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *
from vfx import vfx
import random
from direct.showbase.PythonUtil import fitSrcAngle2Dest

from src.player.base import PlayerBase


class PC4(PlayerBase):
    """Male Magma Mage - magma/teleport attacks."""

    def _setup_actor(self):
        self.actor = Actor("models/pc/male2", {"attack": "models/pc/male2_attack",
                                            "walk": "models/pc/male2_walk",
                                            "block": "models/pc/male2_aura",
                                            "die": "models/pc/male2_die",
                                            "strafe": "models/pc/male2_strafe",
                                            "hit": "models/pc/male2_hit",
                                            "idle": "models/pc/male2_idle"})
        self.actor.setPlayRate(0.5, "strafe")
        self.actor.setScale(.024)
        self.actor.setBin("opaque", 10)

    def _setup_sounds(self):
        self.sounds = {'walk': self.audio3d.loadSfx("sfx/walk_new3.ogg"),
                     'door_open': self.audio3d.loadSfx("sfx/door_open2.ogg"),
                     'door_locked': self.audio3d.loadSfx("sfx/door_locked.ogg"),
                     'key': self.audio3d.loadSfx("sfx/key_pickup.ogg"),
                     'heal': self.audio3d.loadSfx("sfx/heal.ogg"),
                     'hit1': self.audio3d.loadSfx("sfx/hit1.ogg"),
                     'hit2': self.audio3d.loadSfx("sfx/hit2.ogg"),
                     'swing1': self.audio3d.loadSfx("sfx/swing1.ogg"),
                     'swing2': self.audio3d.loadSfx("sfx/swing2.ogg"),
                     'swing3': self.audio3d.loadSfx("sfx/swing3.ogg"),
                     'pain1': self.audio3d.loadSfx("sfx/pain1.ogg"),
                     'pain2': self.audio3d.loadSfx("sfx/pain2.ogg"),
                     'teleport': self.audio3d.loadSfx("sfx/teleport.ogg"),
                     'teleport_fail': self.audio3d.loadSfx("sfx/teleport_fail.ogg"),
                     'block2': self.audio3d.loadSfx("sfx/block2.ogg"),
                     'flame': self.audio3d.loadSfx("sfx/flame2.ogg"),
                     'spell': self.audio3d.loadSfx("sfx/burn2.ogg"),
                     'heal': self.audio3d.loadSfx("sfx/heal3.ogg")
                    }

    def _setup_sounds_extra(self):
        self.magmaSound = base.loader.loadSfx("sfx/magma_flow2.ogg")
        self.magmaSound.setLoop(True)

    def _setup_stats(self):
        self.magma_node = render.attachNewNode("magma_node")
        self.magmaList = []

        self.teleportUp = 0
        self.HP = 40.0
        self.MaxHP = 40.0
        self.speed = 1.0

        self.baseDamage = (50.0 + self.common['pc_stat1']) / 100.0
        self.maxMagma = 1 + int((100 - self.common['pc_stat1']) / 20)
        self.magmaTime = (50.0 + self.common['pc_stat2']) / 100.0
        self.magmaSize = (50.0 + (100.0 - self.common['pc_stat2'])) / 100.0
        self.teleportTime = (100 - self.common['pc_stat3']) / 1000.0
        self.recverTime = (50.0 + (100.0 - self.common['pc_stat3'])) / 100.0

        self.actor.setPlayRate(3.0 * self.recverTime, "block")

        # PC4 also needs these for the destroy method compatibility
        self.damage_delta = 1.0
        self.crit_hit = 0.05
        self.crit_dmg = 5

        self.canTeleport = False
        self.playerHit = False

        self.aura = vfx(self.actor, texture='vfx/aura2.png', scale=.75, Z=.85, depthTest=False, depthWrite=False)
        self.aura.loop(0.02)

    def _get_player_collision_solid(self):
        return CollisionSphere(0, 0, 0.6, 0.5)

    def _setup_pre_collisions(self):
        # Use a different plane Z for PC4
        self.plane = Plane(Vec3(0, 0, 1), Point3(0, 0, 0.1))

    def _setup_collisions_extra(self):
        self.coll_ray2 = self.magma_node.attachNewNode(CollisionNode('collRay'))
        self.coll_ray2.node().addSolid(CollisionRay(0, 0, 2, 0, 0, -180))
        self.coll_ray2.setTag("teleport", "0")
        self.coll_ray2.node().setIntoCollideMask(BitMask32.allOff())
        self.coll_ray2.node().setFromCollideMask(BitMask32.bit(1))
        self.common['traverser'].addCollider(self.coll_ray2, self.common['queue'])

    def _setup_tasks(self):
        taskMgr.doMethodLater(0.05 + self.teleportTime, self.teleport_task, 'teleport_task')
        taskMgr.doMethodLater(0.05, self.magma_task, 'magma_task')
        taskMgr.doMethodLater(0.5, self.magmaDamage, 'magmaDamage')

    def _get_task_names(self):
        return ['teleport_task', 'magma_task', 'magmaDamage']

    def _on_mouse_pos3d(self, pos3d):
        self.magma_node.setPos(pos3d)
        self.magma_node.setZ(0)

    def _handle_collision_entries(self, entry):
        if entry.getFromNodePath().hasTag("magma"):
            status = entry.getFromNodePath().getTag("magma")
            into = entry.getIntoNodePath()
            if status == "1":
                self.magmaDrop()
            if into.hasTag('id'):
                self.hitMonsters.add(into.getTag("id"))
                self.monster_list[int(into.getTag("id"))].lastMagmaDmg = entry.getFromNodePath().getPythonTag("power")
            elif into.hasTag('player'):
                self.playerHit = True
        if entry.getFromNodePath().hasTag("visibility"):
            if entry.getIntoNodePath().hasTag("index"):
                self.myWaypoints.append(int(entry.getIntoNodePath().getTag("index")))
        if entry.getFromNodePath().hasTag("teleport"):
            if entry.getIntoNodePath().hasTag("index"):
                self.canTeleport = True

    def _handle_combat(self, task, dt, anim):
        # Reset per-frame flags
        self.canTeleport = False
        self.playerHit = False
        return None  # Let update handle it fully via our override

    def update(self, task):
        """Override update to handle magma mage specifics."""
        dt = globalClock.getDt()
        self.cameraNode.setPos(self.node.getPos(render))

        #auto camera
        if self.autoCamera and not self.pauseCamera and not self.isOptionsOpen:
            origHpr = self.cameraNode.getHpr()
            targetHpr = self.node.getHpr()
            origHpr = VBase3(fitSrcAngle2Dest(origHpr[0], targetHpr[0]),
                                 fitSrcAngle2Dest(origHpr[1], targetHpr[1]),
                                 fitSrcAngle2Dest(origHpr[2], targetHpr[2]))
            delta = max(abs(targetHpr[0] - origHpr[0]),
                            abs(targetHpr[1] - origHpr[1]),
                            abs(targetHpr[2] - origHpr[2]))
            if delta > 10 and delta < 150 or self.keyMap["key_forward"]:
                t = dt * delta / 2
                if t > .020:
                    t = .020
                t = min(t, 1.0)
                newHpr = origHpr + (targetHpr - origHpr) * t
                self.cameraNode.setHpr(newHpr)
                self.camera_momentum += dt * 3

        if self.camera_momentum > 3.0:
            self.camera_momentum = 3.0
        if self.keyMap["key_cam_right"]:
            self.cameraNode.setH(self.cameraNode, -35 * dt * self.camera_momentum)
            self.camera_momentum += dt * 1.5
        elif self.keyMap["key_cam_left"]:
            self.cameraNode.setH(self.cameraNode, 35 * dt * self.camera_momentum)
            self.camera_momentum += dt * 1.5
        else:
            self.camera_momentum = max(0, self.camera_momentum - dt * 6.0)

        if self.HP <= 0:
            return task.again

        self.common['traverser'].traverse(render)
        hit_wall = False
        self.canTeleport = False
        self.playerHit = False
        self.myWaypoints = []
        for entry in self.common['queue'].getEntries():
            if entry.getFromNodePath().hasTag("player"):
                hit_wall = True
                if entry.getIntoNodePath().hasTag("id"):
                    self.monster_list[int(entry.getIntoNodePath().getTag("id"))].PCisInRange = True
                    hit_wall = False
            if entry.getFromNodePath().hasTag("magma"):
                status = entry.getFromNodePath().getTag("magma")
                into = entry.getIntoNodePath()
                if status == "1":
                    self.magmaDrop()
                if into.hasTag('id'):
                    self.hitMonsters.add(into.getTag("id"))
                    self.monster_list[int(into.getTag("id"))].lastMagmaDmg = entry.getFromNodePath().getPythonTag("power")
                elif into.hasTag('player'):
                    self.playerHit = True
            if entry.getFromNodePath().hasTag("visibility"):
                if entry.getIntoNodePath().hasTag("index"):
                    self.myWaypoints.append(int(entry.getIntoNodePath().getTag("index")))
            if entry.getFromNodePath().hasTag("teleport"):
                if entry.getIntoNodePath().hasTag("index"):
                    self.canTeleport = True

        if hit_wall:
            self.node.setPos(self.lastPos)

        if self.keyMap["key_action2"]:
            if self.teleportUp == -1:
                self.doTeleport()
                self.actor.play("block")
                self.teleportUp = 15

        if self.powerUp > 0:
            self.sounds["walk"].stop()
            if self.actor.getCurrentAnim() != "attack":
                self.actor.loop("attack")
            return task.cont
        else:
            if self.actor.getCurrentAnim() == "attack":
                self.actor.loop("idle")

        anim = self.actor.getCurrentAnim()
        if anim == "attack" or anim == "hit" or anim == "block":
            self.sounds["walk"].stop()
            return task.cont

        #move
        self.lastPos = self.node.getPos(render)
        if self.keyMap["key_forward"]:
            self.isIdle = False
            self.node.setFluidY(self.node, dt * 2)
            self.actor.setPlayRate(1, "walk")
            if self.actor.getCurrentAnim() != "walk":
                self.actor.loop("walk")
                if self.sounds["walk"].status() != self.sounds["walk"].PLAYING:
                    self.sounds["walk"].play()
            if self.keyMap["key_right"]:
                self.node.setFluidX(self.node, dt * 1)
            if self.keyMap["key_left"]:
                self.node.setFluidX(self.node, -dt * 1)
        elif self.keyMap["key_right"]:
            self.isIdle = False
            self.node.setFluidX(self.node, dt * 2)
            self.actor.setPlayRate(-2, "strafe")
            if self.actor.getCurrentAnim() != "strafe":
                self.actor.loop("strafe")
        elif self.keyMap["key_left"]:
            self.isIdle = False
            self.node.setFluidX(self.node, -dt * 2)
            self.actor.setPlayRate(2, "strafe")
            if self.actor.getCurrentAnim() != "strafe":
                self.actor.loop("strafe")
        elif self.keyMap["key_back"]:
            self.isIdle = False
            self.node.setFluidY(self.node, -dt * 2)
            self.actor.setPlayRate(-1, "walk")
            if self.actor.getCurrentAnim() != "walk":
                self.actor.loop("walk")
            if self.sounds["walk"].status() != self.sounds["walk"].PLAYING:
                self.sounds["walk"].play()
        else:
            self.isIdle = True

        if self.isIdle:
            self.sounds["walk"].stop()
            if self.actor.getCurrentAnim() != "idle":
                self.actor.loop("idle")

        return task.cont

    def _destroy_extra(self):
        self.shieldUp = None
        self.blockPower = None
        self.isBlockin = None
        for magma in self.magmaList:
            self.magmaRemove(magma)

    # --- Paladin/Magma Mage-specific methods ---

    def hit(self, damage):
        self.sounds[random.choice(["pain1", "pain2"])].play()
        vfx(self.node, texture='vfx/blood_red.png', scale=.3, Z=1.0, depthTest=True, depthWrite=True).start(0.016)

        self.HP -= damage
        if self.HP <= 0:
            if self.actor.getCurrentAnim() != "die":
                self.actor.play("die")
                self.sounds["walk"].stop()
                self.coll_sphere.node().setFromCollideMask(BitMask32.allOff())
                self.coll_sphere.node().setIntoCollideMask(BitMask32.allOff())
            self.HP = 0
        elif self.actor.getCurrentAnim() != "hit":
            self.actor.play("hit")
        self.healthBar.setScale(10 * self.HP / self.MaxHP, 1, 1)
        green = self.HP / self.MaxHP
        self.healthBar['frameColor'] = (1 - green, green, 0, 1)
        self.sounds["walk"].stop()

    def attack(self, power=1):
        self.attack_ray.node().setFromCollideMask(BitMask32.allOff())
        if self.hitMonsters:
            for monster in self.hitMonsters:
                if monster:
                    monster = self.monster_list[int(monster)]
                    if monster:
                        monster.onHit(power * self.damage_delta)
                        if self.crit_hit > random.random():
                            Sequence(Wait(0.2), Func(monster.onHit, self.crit_dmg)).start()
        self.hitMonsters = set()

    def magmaDamage(self, task):
        if self.hitMonsters:
            for monster in self.hitMonsters:
                if monster and self.monster_list:
                    monster = self.monster_list[int(monster)]
                    if monster:
                        Sequence(Wait(random.uniform(0.0, 0.2)), Func(monster.onMagmaHit)).start()
        if self.playerHit:
            if self.HP <= 0:
                return task.done
            self.sounds['flame'].play()
            vfx(self.node, texture="vfx/small_flame.png", scale=.6, Z=.7, depthTest=False, depthWrite=False).start(0.016, stopAtFrame=24)
            self.HP -= 2.0
            if self.HP <= 0:
                if self.actor.getCurrentAnim() != "die":
                    self.actor.play("die")
                self.sounds["walk"].stop()
                self.coll_sphere.node().setFromCollideMask(BitMask32.allOff())
                self.coll_sphere.node().setIntoCollideMask(BitMask32.allOff())
                self.HP = 0
            self.healthBar.setScale(10 * self.HP / self.MaxHP, 1, 1)
            green = self.HP / self.MaxHP
            self.healthBar['frameColor'] = (1 - green, green, 0, 1)

        self.hitMonsters = set()
        return task.again

    def magmaMover(self, task):
        if self.magmaList[-1].getCurrentAnim() == "flow":
            return task.done
        LerpPosInterval(self.magmaList[-1], 0.6, self.magma_node.getPos()).start()
        LerpHprInterval(self.magmaList[-1], 0.2, self.magmaList[-1].getHpr() + Point3(10, 0, 0)).start()
        return task.again

    def magmaSpawn(self):
        self.sounds['spell'].play()
        self.magmaSound.play()
        magma = Actor("models/lava", {"flow": "models/lava_anim"})
        magma.setBlend(frameBlend=True)
        magma.reparentTo(render)
        magma.setPos(self.magma_node.getPos())
        coll_sphere = magma.attachNewNode(CollisionNode('magmaSphere'))
        coll_sphere.node().addSolid(CollisionSphere(0, 0, 0.4, 0.45))
        coll_sphere.setTag("magma", "1")
        coll_sphere.node().setIntoCollideMask(BitMask32.allOff())
        coll_sphere.node().setFromCollideMask(self.mask_2_3)
        self.common['traverser'].addCollider(coll_sphere, self.common['queue'])
        magma.setPythonTag("collider", coll_sphere)
        magma.setScale(0.3 * self.magmaSize)
        self.magmaList.append(magma)
        taskMgr.doMethodLater(0.2, self.magmaMover, 'magma_task')

    def magmaRemove(self, magma):
        if magma:
            actor_node = self.magmaList.pop(self.magmaList.index(magma))
            collider = actor_node.getPythonTag("collider")
            self.common['traverser'].removeCollider(collider)
            actor_node.cleanup()
            actor_node.removeNode()
            if not self.magmaList:
                self.magmaSound.stop()
                self.sLight.setColor(VBase4(.5, .45, .45, 1))
                self.pLight.setColor(VBase4(.9, .9, 1.0, 1))
                if self.common['extra_ambient']:
                    self.sLight.setColor(VBase4(.7, .6, .6, 1))

    def magmaDrop(self):
        magma = self.magmaList[-1]
        scale = magma.getScale()[0]
        magma.setPlayRate(2.0 - self.magmaTime, "flow")
        magma.play("flow")
        temp = magma.actorInterval("flow", playRate=2.0 - self.magmaTime)
        speed = temp.getDuration()
        magma.wrtReparentTo(render)
        Sequence(Wait(0.6), Func(magma.setZ, render, -0.2)).start()
        collider = magma.getPythonTag("collider")
        collider.setPythonTag("power", self.powerUp * self.baseDamage)
        collider.setTag("magma", "2")
        LerpScaleInterval(collider, speed, scale * 3.0, blendType='easeOut').start()
        Sequence(Wait(speed), Func(self.magmaRemove, magma)).start()
        self.powerUp = 0
        self.cursorPowerUV = [0.0, 0.75]
        self.cursorPower.stateNodePath[0].setTexOffset(TextureStage.getDefault(), self.cursorPowerUV[0], self.cursorPowerUV[1])
        self.keyMap["key_action1"] = False

    def magma_task(self, task):
        if self.HP <= 0:
            return task.done
        if self.keyMap["key_action1"]:
            if len(self.magmaList) > self.maxMagma:
                return task.again
            if self.actor.getCurrentAnim() == "block":
                return task.again
            self.pLight.setColor(VBase4(1.0, .7, .7, 1))
            self.sLight.setColor(VBase4(.55, .35, .35, 1))
            if self.common['extra_ambient']:
                self.sLight.setColor(VBase4(.85, .6, .6, 1))
            if self.powerUp == 0:
                self.magmaSpawn()
            if self.powerUp >= 15:
                return task.again
            self.powerUp += 1
            self.magmaList[-1].setScale(self.magmaList[-1], 1.1)
            self.cursorPowerUV[0] += 0.25
            if self.cursorPowerUV[0] > 0.75:
                self.cursorPowerUV[0] = 0
                self.cursorPowerUV[1] += -0.25
            self.cursorPower.stateNodePath[0].setTexOffset(TextureStage.getDefault(), self.cursorPowerUV[0], self.cursorPowerUV[1])
        else:
            if self.powerUp > 0:
                self.magmaDrop()
        return task.again

    def resetPointer(self):
        p3 = base.cam.getRelativePoint(render, self.node.getPos())
        p2 = Point2()
        newPos = (0, 0, 0)
        if base.camLens.project(p3, p2):
            r2d = Point3(p2[0], 0, p2[1])
            newPos = pixel2d.getRelativePoint(render2d, r2d)
            base.win.movePointer(0, int(newPos[0]), -int(newPos[2]) - 20)

    def resetLight(self):
        if not self.magmaList:
            self.sLight.setColor(VBase4(.5, .45, .45, 1))
            self.pLight.setColor(VBase4(.9, .9, 1.0, 1))
            if self.common['extra_ambient']:
                self.sLight.setColor(VBase4(.7, .6, .6, 1))
        else:
            self.pLight.setColor(VBase4(1.0, .7, .7, 1))
            self.sLight.setColor(VBase4(.55, .35, .35, 1))
            if self.common['extra_ambient']:
                self.sLight.setColor(VBase4(.85, .6, .6, 1))

    def doTeleport(self):
        self.sLight.setColor(VBase4(.4, .4, .6, 1))
        self.pLight.setColor(VBase4(.4, .4, 1.0, 1))
        if self.common['extra_ambient']:
            self.sLight.setColor(VBase4(.5, .5, .7, 1))
        Sequence(Wait(1.0), Func(self.resetLight)).start()
        if self.canTeleport:
            self.sounds['teleport'].play()
            vfx(self.actor, texture='vfx/tele2.png', scale=.5, Z=.85, depthTest=False, depthWrite=False).start()
            self.node.setPos(self.magma_node.getPos())
            Sequence(Wait(0.1), Func(self.resetPointer)).start()
        else:
            self.sounds['teleport_fail'].play()

    def teleport_task(self, task):
        if self.HP <= 0:
            return task.done
        if self.keyMap["key_action2"]:
            if self.teleportUp == -1:
                self.doTeleport()
                self.teleportUp = 15
                return task.again
        if not self.keyMap["key_action2"]:
            if self.teleportUp < 0:
                return task.again
            self.teleportUp -= 1
            self.cursorPowerUV2[0] -= 0.25
            if self.cursorPowerUV2[0] < 0:
                self.cursorPowerUV2[0] = 0.75
                self.cursorPowerUV2[1] += 0.25
            self.cursorPower2.stateNodePath[0].setTexOffset(TextureStage.getDefault(), self.cursorPowerUV2[0], self.cursorPowerUV2[1])
        return task.again
