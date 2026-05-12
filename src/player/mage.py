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
from vfx import MovingVfx
import random

from src.player.base import PlayerBase


class PC2(PlayerBase):
    """Female Mage - plasma/lightning attacks."""

    def _setup_actor(self):
        if self.common['nude']:
            self.actor = Actor("models/pc/female_nude", {"attack1": "models/pc/female_attack1",
                                            "attack2": "models/pc/female_attack2",
                                            "walk": "models/pc/female_run",
                                            "die": "models/pc/female_die",
                                            "strafe": "models/pc/female_strafe",
                                            "hit": "models/pc/female_hit",
                                            "idle": "models/pc/female_idle"})
        else:
            self.actor = Actor("models/pc/female", {"attack1": "models/pc/female_attack1",
                                            "attack2": "models/pc/female_attack2",
                                            "walk": "models/pc/female_run",
                                            "die": "models/pc/female_die",
                                            "strafe": "models/pc/female_strafe",
                                            "hit": "models/pc/female_hit",
                                            "idle": "models/pc/female_idle"})
        self.actor.setPlayRate(1.5, "attack1")
        self.actor.setPlayRate(0.5, "strafe")
        self.actor.setPlayRate(0.7, "die")
        self.actor.setScale(.026)
        self.actor.node().setFinal(True)

    def _setup_sounds(self):
        self.sounds = {'walk': self.audio3d.loadSfx("sfx/walk_new.ogg"),
                     'door_open': self.audio3d.loadSfx("sfx/door_open2.ogg"),
                     'door_locked': self.audio3d.loadSfx("sfx/door_locked.ogg"),
                     'key': self.audio3d.loadSfx("sfx/key_pickup.ogg"),
                     'heal': self.audio3d.loadSfx("sfx/heal.ogg"),
                     'pain1': self.audio3d.loadSfx("sfx/fem_pain1.ogg"),
                     'pain2': self.audio3d.loadSfx("sfx/fem_pain2.ogg"),
                     'plasma_charge': self.audio3d.loadSfx("sfx/plasma_charge.ogg"),
                     'lightning1': self.audio3d.loadSfx("sfx/thunder2.ogg"),
                     'lightning2': self.audio3d.loadSfx("sfx/thunder3.ogg"),
                     'heal': self.audio3d.loadSfx("sfx/heal3.ogg")
                    }

    def _setup_sounds_extra(self):
        self.sounds['plasma_fly'] = self.audio3d.loadSfx("sfx/plasma_fly_loop.ogg")
        self.sounds['plasma_hit'] = self.audio3d.loadSfx("sfx/plasma_hit.ogg")
        self.sounds['plasma_fly'].setLoop(True)

    def _setup_stats(self):
        self.lightningOn = 0
        self.HP = 100.0
        self.MaxHP = 100.0
        self.blockPower = 0.9
        self.blast_size = (self.common['pc_stat1'] + 50) / 100.0
        self.plasma_amp = (75 + (101 - self.common['pc_stat1']) / 2) / 100.0
        self.spark_a = (self.common['pc_stat2'] - 50) / 50.0
        self.spark_b = 14.0 * (self.common['pc_stat2'] - 99.9) / 100.0
        self.power_progress = 1.0 - (self.common['pc_stat3'] / 100.0)
        self.lastPos3d = None
        self.speed = 1.0

    def _get_player_collision_solid(self):
        return CollisionSphere(0, 0, 1, 0.5)

    def _setup_pre_collisions(self):
        self.isLightning = False

    def _setup_collisions_extra(self):
        #lightning ray
        self.hand = self.node.attachNewNode("handNode")
        self.hand.setZ(0.71)
        self.hand.setY(.3)
        self.lightning_vfx = loader.loadModel('vfx/vfx3')
        self.lightning_vfx.setTransparency(TransparencyAttrib.MDual)
        self.lightning_vfx.setBin("fixed", 1)
        self.lightning_vfx.setDepthTest(True)
        self.lightning_vfx.setDepthWrite(True)
        self.lightning_vfx.setLightOff()
        self.lightning_vfx.reparentTo(self.hand)
        self.lightning_vfx.setH(-180)
        self.lightning_vfx.setScale(1, 3.8, 1)
        self.lightning_vfx.hide()
        self.vfxU = 0
        self.vfxV = 0
        self.attack_ray = self.node.attachNewNode(CollisionNode('attackRay'))
        self.attack_ray.node().addSolid(CollisionSegment(0, 0, 0, 0, 0, 12.5))
        self.attack_ray.setTag("attack", "1")
        self.attack_ray.node().setIntoCollideMask(BitMask32.allOff())
        self.attack_ray.node().setFromCollideMask(BitMask32.allOff())
        self.attack_ray.reparentTo(self.hand)
        self.attack_ray.setP(-90)
        self.common['traverser'].addCollider(self.attack_ray, self.common['queue'])

        #plasma
        self.plasma_node = self.node.attachNewNode("plasmaNode")
        self.target_node = render.attachNewNode("plasmaTargetNode")
        self.plasma_node.setZ(0.94)
        self.plasma_node.setY(.32)
        self.plasma_vfx = vfx(self.plasma_node, texture='vfx/plasm2.png', scale=0.05, Z=0, depthTest=True, depthWrite=True)
        self.plasma_vfx.hide()
        self.plasmaLock = False
        self.isBoom = False
        self.projectile = vfx(self.plasma_node, texture='vfx/plasm2.png', scale=0.05, Z=0, depthTest=True, depthWrite=True)
        if 'plasma_coll' in self.common:
            self.plasma_coll = self.common['plasma_coll']
        else:
            self.plasma_coll = render.attachNewNode(CollisionNode('plasmaSphere'))
            self.plasma_coll.node().addSolid(CollisionSphere(0, 0, 0, 0.15))
            self.plasma_coll.setTag("plasma", "1")
            self.plasma_coll.node().setIntoCollideMask(BitMask32.allOff())
            self.plasma_coll.node().setFromCollideMask(BitMask32.allOff())
            self.audio3d.attachSoundToObject(self.sounds['plasma_fly'], self.plasma_coll)
            self.audio3d.attachSoundToObject(self.sounds['plasma_hit'], self.plasma_coll)

        self.common['traverser'].addCollider(self.plasma_coll, self.common['queue'])
        self.lastPower = 0
        self.hitSelf = False

    def _setup_tasks(self):
        taskMgr.doMethodLater(0.05, self.lightning_task, 'lightning_task')
        taskMgr.doMethodLater(0.05, self.plasma_task, 'plasma_task')

    def _get_task_names(self):
        return ['lightning_task', 'plasma_task']

    def _update_auto_camera_extra_check(self):
        return self.isLightning

    def _update_pre_traverse(self, dt):
        if self.projectile.vfx and not self.isBoom:
            self.plasma_coll.setPos(self.projectile.vfx.getPos())

    def _handle_collision_entries(self, entry):
        if entry.getFromNodePath().hasTag("plasma"):
            if entry.getIntoNodePath().hasTag("radar"):
                pass
            else:
                if self.isBoom:
                    if entry.getIntoNodePath().hasTag("id"):
                        self.hitMonsters.add(entry.getIntoNodePath().getTag("id"))
                    if entry.getIntoNodePath().hasTag("player"):
                        self.hitSelf = True
                else:
                    self.boom()

    def _handle_combat(self, task, dt, anim):
        if self.isLightning:
            self.sounds["walk"].stop()
            if self.actor.getCurrentAnim() != "attack1":
                self.actor.play("attack1")
            return task.cont

        if self.powerUp > 0:
            self.sounds["walk"].stop()
            if self.actor.getCurrentAnim() != "idle":
                self.actor.loop("idle")
            return task.cont

        if anim == "attack2" or anim == "hit":
            return task.cont

        return None

    def _on_mouse_pos3d(self, pos3d):
        self.lastPos3d = pos3d
        if self.plasmaLock and self.projectile.vfx:
            self.pLightNode.setPos(self.projectile.vfx.getPos(render))
            self.pLightNode.setZ(2)
        elif self.powerUp > 0:
            self.pLightNode.setPos(self.hand.getPos(render))
            self.pLightNode.setZ(2.7)
        else:
            # Let base handle normal light positioning
            pass
        self.target_node.setPos(pos3d)
        self.target_node.setZ(0.05)

    def __getMousePos(self, task):
        """Override to handle mage-specific mouse behavior."""
        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()
            pos3d = Point3()
            nearPoint = Point3()
            farPoint = Point3()
            base.camLens.extrude(mpos, nearPoint, farPoint)
            if self.plane.intersectsLine(pos3d, render.getRelativePoint(camera, nearPoint), render.getRelativePoint(camera, farPoint)):
                self.lastPos3d = pos3d
                if self.HP > 0:
                    self.node.headsUp(pos3d)
                if self.plasmaLock and self.projectile.vfx:
                    self.pLightNode.setPos(self.projectile.vfx.getPos(render))
                    self.pLightNode.setZ(2)
                elif self.powerUp > 0:
                    self.pLightNode.setPos(self.hand.getPos(render))
                    self.pLightNode.setZ(2.7)
                else:
                    self.pLightNode.setPos(pos3d)
                    self.pLightNode.setZ(2.7)
                self.target_node.setPos(pos3d)
                self.target_node.setZ(0.05)
                if not self.common['safemode']:
                    if self.node.getDistance(self.pLightNode) < 13.0:
                        self.common['shadowNode'].setPos(self.pLightNode.getPos(render))
                        self.common['shadowNode'].setZ(2.7)
            pos2d = Point3(base.mouseWatcherNode.getMouseX(), 0, base.mouseWatcherNode.getMouseY())
            self.cursor.setPos(pixel2d.getRelativePoint(render2d, pos2d))
        return task.again

    def __init__(self, common):
        super().__init__(common)
        # Override the mouse task with our custom one
        taskMgr.remove("mousePosTask")
        taskMgr.add(self.__getMousePos, "mousePosTask")

    def heal(self):
        self.sounds["heal"].play()
        vfx(self.node, texture='vfx/vfx3.png', scale=.8, Z=1.0, depthTest=False, depthWrite=False).start(0.03)
        self.healthBar.setScale(10, 1, 1)
        self.healthBar['frameColor'] = (0, 1, 0, 1)
        self.HP = 100.0

    def _destroy_extra(self):
        self.lightning_vfx.removeNode()
        self.lightningOn = None
        self.blockPower = None
        self.isLightning = None
        self.common['traverser'].removeCollider(self.attack_ray)
        self.common['traverser'].removeCollider(self.plasma_coll)
        self.attack_ray.removeNode()
        self.common['plasma_coll'] = self.plasma_coll

    # --- Mage-specific methods ---

    def hit(self, damage):
        self.sounds[random.choice(["pain1", "pain2"])].play()
        vfx(self.node, texture='vfx/blood_red.png', scale=.3, Z=1.0, depthTest=True, depthWrite=True).start(0.016)

        self.HP -= damage * 2
        if self.HP <= 0:
            if self.actor.getCurrentAnim() != "die":
                self.actor.play("die")
                self.sounds["walk"].stop()
                self.coll_sphere.node().setFromCollideMask(BitMask32.allOff())
                self.coll_sphere.node().setIntoCollideMask(BitMask32.allOff())
            self.HP = 0
        else:
            if self.actor.getCurrentAnim() != "hit":
                self.actor.play("hit")
        self.healthBar.setScale(self.HP / 10.0, 1, 1)
        green = self.HP / 100.0
        self.healthBar['frameColor'] = (1 - green, green, 0, 1)
        self.sounds["walk"].stop()

    def spark_dmg(self, power, distance):
        pow = (8.0 * self.power_progress + power * (1.0 - self.power_progress)) / 2.0
        return pow * int(distance * self.spark_a - self.spark_b) / 6.0

    def spark_attack(self, power=1):
        if self.hitMonsters:
            for monster in self.hitMonsters:
                if monster:
                    monster = self.monster_list[int(monster)]
                    if monster:
                        dist = self.node.getDistance(monster.node)
                        monster.onSparkHit(self.spark_dmg(power, dist))
        self.hitMonsters = set()

    def plasma_dmg(self, power):
        final = (power + 5) * self.power_progress + ((power + 5) * (power + 5) / 15.0) * (1.0 - self.power_progress)
        return self.plasma_amp * final

    def plasma_attack(self, power=1):
        if self.hitMonsters:
            for monster in self.hitMonsters:
                if monster:
                    monster = self.monster_list[int(monster)]
                    if monster:
                        monster.onPlasmaHit(2 * self.plasma_dmg(power))
        self.hitMonsters = set()

    def end_boom(self):
        self.isBoom = False
        self.plasmaLock = False
        self.pLight.setColor(VBase4(.9, .9, 1.0, 1))
        self.pLight.setAttenuation(Point3(2, 0, 0.5))
        self.plasma_coll.setScale(1)
        self.plasma_attack(self.lastPower)
        if self.hitSelf:
            self.hit(self.lastPower / 2)
        self.hitSelf = False
        self.plasma_coll.node().setFromCollideMask(BitMask32.allOff())

    def boom(self):
        vfx_node = self.projectile.vfx
        scale = self.blast_size * (self.lastPower + 1) / 15.0
        if self.isBoom:
            return
        self.isBoom = True
        self.pLight.setColor(VBase4(.35, .3, 1, 1))
        self.sounds['plasma_fly'].stop()
        self.sounds['plasma_hit'].play()
        self.plasma_coll.setScale(10 * scale)
        if vfx_node:
            vfx_node.hide()
            vfx(None, texture='vfx/m_blast.png', scale=scale, Z=0.0, depthTest=True, depthWrite=True, pos=vfx_node.getPos(render)).start(0.016)
            Sequence(Wait(0.6), Func(self.end_boom)).start()

    def arm_plasma(self):
        self.plasma_coll.node().setFromCollideMask(self.mask_2_3)

    def resetPointer(self, point3D):
        p3 = base.cam.getRelativePoint(render, point3D)
        p2 = Point2()
        newPos = (0, 0, 0)
        if base.camLens.project(p3, p2):
            r2d = Point3(p2[0], 0, p2[1])
            newPos = pixel2d.getRelativePoint(render2d, r2d)
            base.win.movePointer(0, int(newPos[0]), -int(newPos[2]))

    def plasma_task(self, task):
        if self.HP <= 0:
            return task.done
        if self.isLightning:
            return task.again
        if self.keyMap["key_action1"] and not self.plasmaLock:
            l = (self.powerUp + 1) / 25.0
            self.pLight.setColor(VBase4(l, l, l * 1.5, 1))
            self.pLight.setAttenuation(Point3(0, 0, 1 - l * 1.2))
            if self.powerUp == 0:
                if self.autoCamera and not self.pauseCamera and not self.isOptionsOpen:
                    if abs(self.cameraNode.getH() - self.node.getH()) > 90.0:
                        reset_pos = self.lastPos3d
                        Sequence(LerpHprInterval(self.cameraNode, 0.2, self.node.getHpr()), Func(self.resetPointer, reset_pos)).start()
                self.plasma_vfx.show()
                self.plasma_vfx.loop(0.015)
                self.sounds['plasma_charge'].play()
            if self.powerUp >= 15:
                return task.again
            self.plasma_vfx.vfx.setScale((self.powerUp + 1) / 3.0)
            self.powerUp += 1
            self.cursorPowerUV[0] += 0.25
            if self.cursorPowerUV[0] > 0.75:
                self.cursorPowerUV[0] = 0
                self.cursorPowerUV[1] += -0.25
            self.cursorPower.stateNodePath[0].setTexOffset(TextureStage.getDefault(), self.cursorPowerUV[0], self.cursorPowerUV[1])
        else:
            if self.powerUp > 0:
                self.sounds["walk"].stop()
                self.actor.play("attack2")
                self.plasma_vfx.stop()
                self.projectile = MovingVfx(self.plasma_node, self.target_node, texture='vfx/plasm2.png', scale=0.05, Z=0.0, time=.6, gravity=.55, depthTest=True, depthWrite=True)
                self.projectile.start()
                self.sounds['plasma_fly'].play()
                self.projectile.vfx.setScale((self.powerUp + 1) / 3.0)
                self.lastPower = self.powerUp
                Sequence(Wait(0.1), Func(self.arm_plasma), Wait(0.4), Func(self.boom)).start()
                self.plasmaLock = True
            self.powerUp = 0
            self.cursorPowerUV = [0.0, 0.75]
            self.cursorPower.stateNodePath[0].setTexOffset(TextureStage.getDefault(), self.cursorPowerUV[0], self.cursorPowerUV[1])
        return task.again

    def lightning_task(self, task):
        if self.HP <= 0:
            self.lightning_vfx.hide()
            if self.common['extra_ambient']:
                self.sLight.setColor(VBase4(.7, .6, .6, 1))
            else:
                self.sLight.setColor(VBase4(.5, .45, .45, 1))
            return task.done
        if self.keyMap["key_action2"]:
            if self.lightningOn >= 15:
                self.isLightning = False
                self.lightning_vfx.hide()
                self.attack_ray.node().setFromCollideMask(BitMask32.allOff())
                if self.common['extra_ambient']:
                    self.sLight.setColor(VBase4(.7, .6, .6, 1))
                else:
                    self.sLight.setColor(VBase4(.5, .45, .45, 1))
                return task.again
            if self.lightningOn == -1:
                self.sounds[random.choice(["lightning1", "lightning2"])].play()
                self.attack_ray.node().setFromCollideMask(BitMask32.bit(3))
                self.actor.play("attack1")
            if self.lightningOn % 2 == 0:
                r = random.uniform(0.2, 0.5)
                self.sLight.setColor(VBase4(r, r, 1, 1))
            else:
                if self.common['extra_ambient']:
                    self.sLight.setColor(VBase4(.7, .6, .6, 1))
                else:
                    self.sLight.setColor(VBase4(.5, .45, .45, 1))
            self.isLightning = True
            self.lightningOn += 1
            self.lightning_vfx.show()
            self.cursorPowerUV2[0] += 0.25
            if self.cursorPowerUV2[0] > 0.75:
                self.cursorPowerUV2[0] = 0
                self.cursorPowerUV2[1] += -0.25
            self.cursorPower2.stateNodePath[0].setTexOffset(TextureStage.getDefault(), self.cursorPowerUV2[0], self.cursorPowerUV2[1])
            self.vfxU = self.vfxU + 0.5
            if self.vfxU >= 1.0:
                self.vfxU = 0
                self.vfxV = self.vfxV - 0.125
            if self.vfxV <= -1:
                self.vfxU = 0
                self.vfxV = 0
            self.lightning_vfx.setTexOffset(TextureStage.getDefault(), self.vfxU, self.vfxV)
            self.spark_attack(self.lightningOn)
        else:
            self.isLightning = False
            self.lightning_vfx.hide()
            self.attack_ray.node().setFromCollideMask(BitMask32.allOff())
            if self.common['extra_ambient']:
                self.sLight.setColor(VBase4(.7, .6, .6, 1))
            else:
                self.sLight.setColor(VBase4(.5, .45, .45, 1))
            if self.lightningOn < 0:
                return task.again
            self.lightningOn -= 1
            self.cursorPowerUV2[0] -= 0.25
            if self.cursorPowerUV2[0] < 0:
                self.cursorPowerUV2[0] = 0.75
                self.cursorPowerUV2[1] += 0.25
            self.cursorPower2.stateNodePath[0].setTexOffset(TextureStage.getDefault(), self.cursorPowerUV2[0], self.cursorPowerUV2[1])
        return task.again
