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


class PC3(PlayerBase):
    """Female Archer/Ranger - bow and arrows."""

    def _setup_actor(self):
        if self.common['nude']:
            self.actor = Actor("models/pc/female2_nude", {"arm": "models/pc/female2_arm",
                                            "fire": "models/pc/female2_fire",
                                            "walk": "models/pc/female2_run",
                                            "run": "models/pc/female2_run2",
                                            "die": "models/pc/female2_die",
                                            "strafe": "models/pc/female2_strafe",
                                            "hit": "models/pc/female2_hit",
                                            "idle": "models/pc/female2_idle"})
        else:
            self.actor = Actor("models/pc/female2", {"arm": "models/pc/female2_arm",
                                                "fire": "models/pc/female2_fire",
                                                "walk": "models/pc/female2_run",
                                                "run": "models/pc/female2_run2",
                                                "die": "models/pc/female2_die",
                                                "strafe": "models/pc/female2_strafe",
                                                "hit": "models/pc/female2_hit",
                                                "idle": "models/pc/female2_idle"})
        self.actor.setPlayRate(0.5, "strafe")
        self.actor.setPlayRate(1.5, "fire")
        self.actor.setScale(.026)
        self.actor.setBin("opaque", 10)

    def _setup_sounds(self):
        self.sounds = {'walk': self.audio3d.loadSfx("sfx/walk_new.ogg"),
                     'door_open': self.audio3d.loadSfx("sfx/door_open2.ogg"),
                     'door_locked': self.audio3d.loadSfx("sfx/door_locked.ogg"),
                     'key': self.audio3d.loadSfx("sfx/key_pickup.ogg"),
                     'pain1': self.audio3d.loadSfx("sfx/fem_pain1.ogg"),
                     'pain2': self.audio3d.loadSfx("sfx/fem_pain2.ogg"),
                     'heal': self.audio3d.loadSfx("sfx/heal3.ogg"),
                     'fire': self.audio3d.loadSfx("sfx/fire_arrow3.ogg"),
                     'arm': self.audio3d.loadSfx("sfx/draw_bow3.ogg"),
                     'run': self.audio3d.loadSfx("sfx/run3.ogg"),
                    }

    def _setup_sounds_extra(self):
        self.sounds['run'].setLoop(True)

    def _setup_stats(self):
        self.runUp = 0
        self.HP = 70.0
        self.MaxHP = 70.0
        self.barbChance = int(self.common['pc_stat1'] / 2)
        self.pierceChance = int((100 - self.common['pc_stat1']) / 2)
        self.bleedSlowRatio = int(self.common['pc_stat2'])
        self.critChance = 25 + int(self.common['pc_stat3'] / 2)
        print(self.critChance)
        self.baseDamage = (50 + int(100 - self.common['pc_stat3'])) / 100.0
        self.speed = .8
        self.isRunning = False
        self.lastPos3d = None

        self.arrow_bone = self.actor.exposeJoint(None, 'modelRoot', 'arrow_bone')
        self.arrow = loader.loadModel('models/arrow')
        self.arrow.reparentTo(self.arrow_bone)
        self.arrows = []

        self.damage_delta = (1.0 + self.common['pc_stat3'] / 50.0)
        self.crit_hit = (5 + (101 - self.common['pc_stat3']) / 2) / 100.0
        self.crit_dmg = 5 + (101 - self.common['pc_stat3']) / 5

    def _get_player_collision_solid(self):
        return CollisionSphere(0, 0, 1, 0.4)

    def _setup_pre_collisions(self):
        self.isRunning = False

    def _setup_collisions_extra(self):
        self.arrowSpheres = []
        self.freeArrowSpheres = []
        for i in range(8):
            self.arrowSpheres.append(render.attachNewNode(CollisionNode('arrow' + str(i))))
            self.arrowSpheres[-1].node().addSolid(CollisionSphere(0, 0, 0, 0.1))
            self.arrowSpheres[-1].setTag("arrow", str(i))
            self.arrowSpheres[-1].node().setIntoCollideMask(BitMask32.allOff())
            self.arrowSpheres[-1].node().setFromCollideMask(BitMask32.allOff())
            self.freeArrowSpheres.append(i)
            self.common['traverser'].addCollider(self.arrowSpheres[-1], self.common['queue'])

    def _setup_tasks(self):
        taskMgr.doMethodLater(0.05, self.run_task, 'run_task')
        taskMgr.doMethodLater(0.05, self.bow_task, 'bow_task')

    def _get_task_names(self):
        return ['run_task', 'bow_task', 'regenerate_task']

    def _on_mouse_pos3d(self, pos3d):
        self.lastPos3d = pos3d

    def _handle_collision_entries(self, entry):
        if entry.getFromNodePath().hasTag('arrow'):
            arrow = entry.getFromNodePath().getPythonTag('arrow')
            if entry.getIntoNodePath().hasTag("id"):
                self.attack(arrow, self.monster_list[int(entry.getIntoNodePath().getTag("id"))])
                self.stickArrow(arrow, self.monster_list[int(entry.getIntoNodePath().getTag("id"))])
            elif entry.getIntoNodePath().hasTag("player"):
                pass
            else:
                self.stickArrow(arrow)

    def _update_pre_traverse(self, dt):
        # Update arrow positions
        newArrowsArray = []
        for arrow in self.arrows:
            power = self.getArrowPower(arrow)
            arrow.setFluidX(arrow, power[0] * dt)
            arrow.setR(arrow, power[1] * dt)
            if self.getExpires(arrow, dt):
                self.removeArrow(arrow)
            else:
                newArrowsArray.append(arrow)
        self.arrows = newArrowsArray

    def _handle_combat(self, task, dt, anim):
        if anim == "fire" or anim == "arm" or anim == "hit":
            return task.cont

        if self.powerUp > 0:
            return task.cont

        return None

    def _update_movement_speed(self):
        return (4 * self.speed, 3 * self.speed, 4 * self.speed, 1, -0.8)

    def update(self, task):
        """Override update to handle running."""
        dt = globalClock.getDt()
        self.cameraNode.setPos(self.node.getPos(render))

        self._update_pre_traverse(dt)

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
            if delta > 20 and delta < 150 or self.keyMap["key_forward"]:
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
        self.myWaypoints = []
        for entry in self.common['queue'].getEntries():
            self._handle_collision_entries(entry)
            if entry.getFromNodePath().hasTag("player"):
                hit_wall = True
                if entry.getIntoNodePath().hasTag("id"):
                    self.monster_list[int(entry.getIntoNodePath().getTag("id"))].PCisInRange = True
                    hit_wall = False
            if entry.getFromNodePath().hasTag("attack"):
                self.hitMonsters.add(entry.getIntoNodePath().getTag("id"))
            if entry.getIntoNodePath().hasTag("index"):
                self.myWaypoints.append(int(entry.getIntoNodePath().getTag("index")))

        if hit_wall:
            self.node.setPos(self.lastPos)

        anim = self.actor.getCurrentAnim()
        if anim == "fire" or anim == "arm" or anim == "hit":
            return task.cont

        if self.powerUp > 0:
            return task.cont

        #move
        self.lastPos = self.node.getPos(render)
        if self.keyMap["key_forward"]:
            self.isIdle = False
            if self.isRunning:
                self.node.setFluidY(self.node, dt * 7)
                if self.actor.getCurrentAnim() != "run":
                    self.actor.loop("run")
                    if self.sounds["walk"].status() == self.sounds["walk"].PLAYING:
                        self.sounds["walk"].stop()
                    if self.sounds["run"].status() != self.sounds["run"].PLAYING:
                        self.sounds["run"].play()
            else:
                self.node.setFluidY(self.node, dt * 4 * self.speed)
                self.actor.setPlayRate(1, "walk")
                if self.actor.getCurrentAnim() != "walk":
                    self.actor.loop("walk")
                    if self.sounds["walk"].status() != self.sounds["walk"].PLAYING:
                        self.sounds["walk"].play()
            if self.keyMap["key_right"]:
                self.node.setFluidX(self.node, dt * 1 * self.speed)
            if self.keyMap["key_left"]:
                self.node.setFluidX(self.node, -dt * 1 * self.speed)
        elif self.keyMap["key_right"]:
            self.isIdle = False
            self.node.setFluidX(self.node, dt * 4 * self.speed)
            self.actor.setPlayRate(-2, "strafe")
            if self.actor.getCurrentAnim() != "strafe":
                self.actor.loop("strafe")
        elif self.keyMap["key_left"]:
            self.isIdle = False
            self.node.setFluidX(self.node, -dt * 4 * self.speed)
            self.actor.setPlayRate(2, "strafe")
            if self.actor.getCurrentAnim() != "strafe":
                self.actor.loop("strafe")
        elif self.keyMap["key_back"]:
            self.isIdle = False
            self.node.setFluidY(self.node, -dt * 3 * self.speed)
            self.actor.setPlayRate(-0.8, "walk")
            if self.actor.getCurrentAnim() != "walk":
                self.actor.loop("walk")
            if self.sounds["walk"].status() != self.sounds["walk"].PLAYING:
                self.sounds["walk"].play()
        else:
            self.isIdle = True

        if not self.isRunning:
            if self.sounds["run"].status() == self.sounds["run"].PLAYING:
                self.sounds["run"].stop()

        if self.isIdle:
            self.sounds["walk"].stop()
            if self.actor.getCurrentAnim() != "idle":
                self.actor.loop("idle")

        return task.cont

    def _destroy_extra(self):
        self.shieldUp = None
        self.blockPower = None
        self.isRunning = None
        for sphere in self.arrowSpheres:
            self.common['traverser'].removeCollider(sphere)
            sphere.removeNode()

    # --- Ranger-specific methods ---

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
        else:
            if self.actor.getCurrentAnim() != "hit":
                self.actor.play("hit")
        self.healthBar.setScale(10 * self.HP / self.MaxHP, 1, 1)
        green = self.HP / self.MaxHP
        self.healthBar['frameColor'] = (1 - green, green, 0, 1)
        self.sounds["walk"].stop()

    def attack(self, arrow, monster):
        if arrow:
            if arrow in monster.arrows:
                return
            else:
                monster.arrows.add(arrow)
            power = arrow.getPythonTag('power')[2]
            damage = power * self.baseDamage
            monster.onHit(damage, "arrow_hit")
            barb_roll = random.randrange(0, 101)
            crit_roll = random.randrange(0, 101)
            barb = False
            if self.barbChance > barb_roll:
                barb = True
                Sequence(Wait(0.2), Func(monster.onHit, damage, None)).start()
            if crit_roll + power > self.critChance:
                effect_roll = random.randrange(0, 101)
                if effect_roll >= self.bleedSlowRatio:
                    if monster.totalSpeed < 0.5:
                        monster.DOT += power / 4.0
                    if barb:
                        monster.totalSpeed = monster.totalSpeed * 0.8
                    else:
                        monster.totalSpeed = monster.totalSpeed * 0.9
                else:
                    if barb:
                        monster.DOT += power
                    else:
                        monster.DOT += power / 2.0

    def getExpires(self, obj, delta):
        ttl = 0.0
        if obj.hasPythonTag('TTL'):
            ttl = obj.getPythonTag('TTL')
        ttl += delta
        if ttl > 1.0:
            return True
        else:
            obj.setPythonTag('TTL', ttl)
            return False

    def getArrowPower(self, arrow):
        return arrow.getPythonTag('power')

    def resetCollideMask(self, collider, mask):
        collider.node().setFromCollideMask(mask)

    def stickArrow(self, arrow, target=None):
        if arrow:
            collider = arrow.getPythonTag('collider')
            roll = random.randrange(0, 101)
            if target == None:
                collider.wrtReparentTo(render)
                collider.node().setFromCollideMask(BitMask32.allOff())
                collider.setPythonTag('arrow', None)
                id = collider.getTag('arrow')
                self.freeArrowSpheres.append(int(id))
                self.arrows.pop(self.arrows.index(arrow))
                arrow.wrtReparentTo(render)
                Sequence(Wait(10.0), Func(arrow.removeNode)).start()
            elif self.pierceChance < roll:
                if arrow.hasPythonTag('pierce'):
                    return
                collider.wrtReparentTo(render)
                collider.node().setFromCollideMask(BitMask32.allOff())
                collider.setPythonTag('arrow', None)
                id = collider.getTag('arrow')
                self.freeArrowSpheres.append(int(id))
                self.arrows.pop(self.arrows.index(arrow))
                arrow.wrtReparentTo(target.rootBone)
                Sequence(Wait(10.0), Func(arrow.removeNode)).start()
            else:
                arrow.setPythonTag('pierce', 1)

    def removeArrow(self, arrow):
        if arrow:
            collider = arrow.getPythonTag('collider')
            collider.wrtReparentTo(render)
            collider.node().setFromCollideMask(BitMask32.allOff())
            collider.setPythonTag('arrow', None)
            id = collider.getTag('arrow')
            self.freeArrowSpheres.append(int(id))
            arrow.removeNode()

    def fireArrow(self, power):
        newArrow = loader.loadModel('models/arrow')
        newArrow.reparentTo(self.arrow_bone)
        newArrow.setP(-45)
        newArrow.wrtReparentTo(render)
        newArrow.setLightOff()
        newArrow.setPythonTag('power', [power * 80, 10.0 + 150.0 / power, power])

        collider = self.arrowSpheres[self.freeArrowSpheres.pop()]
        collider.setPos(render, newArrow.getPos())
        collider.wrtReparentTo(newArrow)
        collider.node().setFromCollideMask(self.mask_2_3)
        collider.setPythonTag('arrow', newArrow)

        newArrow.setPythonTag('collider', collider)

        self.arrow.hide()
        self.arrows.append(newArrow)
        Sequence(Wait(0.5), Func(self.arrow.show)).start()

    def resetPointer(self, point3D):
        p3 = base.cam.getRelativePoint(render, point3D)
        p2 = Point2()
        newPos = (0, 0, 0)
        if base.camLens.project(p3, p2):
            r2d = Point3(p2[0], 0, p2[1])
            newPos = pixel2d.getRelativePoint(render2d, r2d)
            base.win.movePointer(0, int(newPos[0]), -int(newPos[2]))

    def bow_task(self, task):
        if self.HP <= 0:
            return task.done
        if self.isRunning:
            return task.again
        if self.keyMap["key_action1"]:
            if self.powerUp >= 15:
                return task.again
            if self.powerUp == 1:
                if self.autoCamera and not self.pauseCamera and not self.isOptionsOpen:
                    if abs(self.cameraNode.getH() - self.node.getH()) > 90.0:
                        reset_pos = self.lastPos3d
                        Sequence(LerpHprInterval(self.cameraNode, 0.2, self.node.getHpr()), Func(self.resetPointer, reset_pos)).start()
                self.actor.play("arm")
                self.sounds["arm"].play()
                if self.sounds["walk"].status() == self.sounds["walk"].PLAYING:
                    self.sounds["walk"].stop()
            self.powerUp += 1
            self.cursorPowerUV[0] += 0.25
            if self.cursorPowerUV[0] > 0.75:
                self.cursorPowerUV[0] = 0
                self.cursorPowerUV[1] += -0.25
            self.cursorPower.stateNodePath[0].setTexOffset(TextureStage.getDefault(), self.cursorPowerUV[0], self.cursorPowerUV[1])
        else:
            if self.powerUp > 2:
                self.actor.play("fire")
                self.sounds["fire"].play()
                self.fireArrow(self.powerUp)
                self.pauseCamera = False
            self.powerUp = 0
            self.cursorPowerUV = [0.0, 0.75]
            self.cursorPower.stateNodePath[0].setTexOffset(TextureStage.getDefault(), self.cursorPowerUV[0], self.cursorPowerUV[1])
        return task.again

    def run_task(self, task):
        if self.HP <= 0:
            return task.done
        if self.keyMap["key_action2"]:
            if self.runUp >= 15:
                self.isRunning = False
                return task.again
            self.isRunning = True
            self.runUp += 1
            self.cursorPowerUV2[0] += 0.25
            if self.cursorPowerUV2[0] > 0.75:
                self.cursorPowerUV2[0] = 0
                self.cursorPowerUV2[1] += -0.25
            self.cursorPower2.stateNodePath[0].setTexOffset(TextureStage.getDefault(), self.cursorPowerUV2[0], self.cursorPowerUV2[1])
        else:
            self.isRunning = False
            if self.runUp < 0:
                return task.again
            self.runUp -= 1
            self.cursorPowerUV2[0] -= 0.25
            if self.cursorPowerUV2[0] < 0:
                self.cursorPowerUV2[0] = 0.75
                self.cursorPowerUV2[1] += 0.25
            self.cursorPower2.stateNodePath[0].setTexOffset(TextureStage.getDefault(), self.cursorPowerUV2[0], self.cursorPowerUV2[1])
        return task.again
