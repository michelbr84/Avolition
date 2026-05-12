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

from src.player.base import PlayerBase


class PC1(PlayerBase):
    """Sword Warrior - male model, melee combat with sword and shield."""

    def _setup_actor(self):
        self.actor = Actor("models/pc/male", {"attack1": "models/pc/male_attack1",
                                            "attack2": "models/pc/male_attack2",
                                            "walk": "models/pc/male_run",
                                            "block": "models/pc/male_block",
                                            "die": "models/pc/male_die",
                                            "strafe": "models/pc/male_strafe2",
                                            "hit": "models/pc/male_hit",
                                            "idle": "models/pc/male_ready2"})
        self.actor.setPlayRate(1.5, "attack1")
        self.actor.setPlayRate(0.5, "strafe")
        self.actor.setPlayRate(0.7, "die")
        self.actor.setScale(.025)
        self.actor.setBin("opaque", 10)

    def _setup_sounds(self):
        self.sounds = {'walk': self.audio3d.loadSfx("sfx/walk_new.ogg"),
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
                     'block1': self.audio3d.loadSfx("sfx/block1.ogg"),
                     'block2': self.audio3d.loadSfx("sfx/block2.ogg"),
                     'heal': self.audio3d.loadSfx("sfx/heal3.ogg")
                    }

    def _setup_stats(self):
        self.shieldUp = 0
        self.HP = 50.0 + float(self.common['pc_stat1'])
        self.MaxHP = 50.0 + float(self.common['pc_stat1'])
        self.HPregen = round((101 - self.common['pc_stat1']) / 100.0, 1)
        self.blockPower = (50 + (self.common['pc_stat2'] + 1) / 2) / 100.0
        self.speed = (75 + (101 - self.common['pc_stat2']) / 2) / 100.0
        self.actor.setPlayRate(self.speed, "walk")
        self.damage_delta = (1.0 + self.common['pc_stat3'] / 50.0)
        self.crit_hit = (5 + (101 - self.common['pc_stat3']) / 2) / 100.0
        self.crit_dmg = 5 + (101 - self.common['pc_stat3']) / 5

    def _setup_pre_collisions(self):
        self.isBlockin = False

    def _get_player_collision_solid(self):
        return CollisionSphere(0, 0, 1, 0.4)

    def _setup_collisions_extra(self):
        hand = self.actor.exposeJoint(None, 'modelRoot', 'Bip001 R Hand')
        self.attack_ray = self.node.attachNewNode(CollisionNode('attackRay'))
        self.attack_ray.node().addSolid(CollisionSegment(0, 0, 0, 0, 0, 24))
        self.attack_ray.setTag("attack", "1")
        self.attack_ray.node().setIntoCollideMask(BitMask32.allOff())
        self.attack_ray.node().setFromCollideMask(BitMask32.allOff())
        self.attack_ray.reparentTo(hand)
        self.attack_ray.setX(self.attack_ray, 3)
        self.attack_ray.setHpr(self.attack_ray, (0, -5, -2))
        self.common['traverser'].addCollider(self.attack_ray, self.common['queue'])

    def _setup_tasks(self):
        taskMgr.doMethodLater(0.05, self.shield_task, 'shield_task')
        taskMgr.doMethodLater(0.05, self.sword_task, 'sword_task')
        taskMgr.doMethodLater(1.0, self.regenerate, 'regenerate_task')

    def _get_task_names(self):
        return ['shield_task', 'sword_task', 'regenerate_task']

    def _update_movement_speed(self):
        return (4 * self.speed, 3 * self.speed, 4 * self.speed, 1 * self.speed, -0.8 * self.speed)

    def _handle_combat(self, task, dt, anim):
        if self.isBlockin:
            self.sounds["walk"].stop()
            if self.actor.getCurrentAnim() != "block":
                self.actor.loop("block")
            return task.cont

        if anim == "attack1" or anim == "attack2" or anim == "hit":
            return task.cont

        return None

    def _destroy_extra(self):
        self.shieldUp = None
        self.blockPower = None
        self.isBlockin = None
        self.common['traverser'].removeCollider(self.attack_ray)
        self.attack_ray.removeNode()

    # --- Warrior-specific methods ---

    def regenerate(self, task):
        if self.MaxHP > self.HP > 0:
            self.HP += self.HPregen
            self.healthBar.setScale(10 * self.HP / self.MaxHP, 1, 1)
            green = self.HP / self.MaxHP
            self.healthBar['frameColor'] = (1 - green, green, 0, 1)
        return task.again

    def hit(self, damage):
        if self.isBlockin:
            self.sounds[random.choice(["block1", "block2"])].play()
            damage = damage * (1 - self.blockPower)
            if damage < 0:
                damage = 0
        else:
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
        elif not self.isBlockin:
            if self.actor.getCurrentAnim() != "hit":
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

    def sword_task(self, task):
        if self.HP <= 0:
            return task.done
        if self.isBlockin:
            return task.again
        if self.keyMap["key_action1"]:
            if self.powerUp >= 15:
                return task.again
            self.powerUp += 1
            self.cursorPowerUV[0] += 0.25
            if self.cursorPowerUV[0] > 0.75:
                self.cursorPowerUV[0] = 0
                self.cursorPowerUV[1] += -0.25
            self.cursorPower.stateNodePath[0].setTexOffset(TextureStage.getDefault(), self.cursorPowerUV[0], self.cursorPowerUV[1])
        else:
            if self.powerUp > 8:
                self.sounds["walk"].stop()
                self.actor.play("attack2")
                self.sounds["swing2"].play()
                self.attack_ray.node().setFromCollideMask(BitMask32.bit(3))
                Sequence(Wait(.3), Func(self.attack, self.powerUp)).start()
            elif self.powerUp > 0:
                self.sounds["walk"].stop()
                self.actor.play("attack1")
                self.sounds["swing1"].play()
                self.attack_ray.node().setFromCollideMask(BitMask32.bit(3))
                Sequence(Wait(.2), Func(self.attack, self.powerUp)).start()
            self.powerUp = 0
            self.cursorPowerUV = [0.0, 0.75]
            self.cursorPower.stateNodePath[0].setTexOffset(TextureStage.getDefault(), self.cursorPowerUV[0], self.cursorPowerUV[1])
        return task.again

    def unBlock(self):
        self.isBlockin = False

    def shield_task(self, task):
        if self.HP <= 0:
            return task.done
        if self.keyMap["key_action2"]:
            if self.shieldUp >= 15:
                Sequence(Wait(0.3), Func(self.unBlock)).start()
                return task.again
            self.isBlockin = True
            self.shieldUp += 1
            self.cursorPowerUV2[0] += 0.25
            if self.cursorPowerUV2[0] > 0.75:
                self.cursorPowerUV2[0] = 0
                self.cursorPowerUV2[1] += -0.25
            self.cursorPower2.stateNodePath[0].setTexOffset(TextureStage.getDefault(), self.cursorPowerUV2[0], self.cursorPowerUV2[1])
        else:
            self.isBlockin = False
            if self.shieldUp < 0:
                return task.again
            self.shieldUp -= 1
            self.cursorPowerUV2[0] -= 0.25
            if self.cursorPowerUV2[0] < 0:
                self.cursorPowerUV2[0] = 0.75
                self.cursorPowerUV2[1] += 0.25
            self.cursorPower2.stateNodePath[0].setTexOffset(TextureStage.getDefault(), self.cursorPowerUV2[0], self.cursorPowerUV2[1])
        return task.again
