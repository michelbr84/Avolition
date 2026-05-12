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
from direct.showbase.DirectObject import DirectObject
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *
from direct.filter.FilterManager import FilterManager
from direct.gui.DirectGui import *
from vfx import vfx
from vfx import MovingVfx
import random
from direct.showbase.PythonUtil import fitSrcAngle2Dest


class PlayerBase(DirectObject):
    """Base class for all player characters.

    Subclasses must override:
        _setup_actor(self)         - create self.actor with animations
        _setup_sounds(self)        - populate self.sounds dict with class-specific sounds
        _setup_stats(self)         - set HP, MaxHP, speed, damage, etc.
        _setup_collisions_extra(self) - set up class-specific collision nodes
        _setup_tasks(self)         - register class-specific tasks (doMethodLater)
        _get_task_names(self)      - return list of class-specific task names for cleanup
        _destroy_extra(self)       - clean up class-specific resources
        _handle_combat(self, task, dt, anim) - handle class-specific combat in update loop
        _handle_collision_entries(self, entry) - process class-specific collision entries
        hit(self, damage)          - handle taking damage (varies per class)
    """

    def onLevelLoad(self, common):
        self.node.setPos(0, 0, 0)
        self.black = common['map_black']
        self.walls = common['map_walls']
        self.floor = common['map_floor']
        self.monster_list = common['monsterList']
        if not self.common['safemode']:
            wall_shader = loader.loadShader('assets/shaders/tiles.sha')
            black_shader = loader.loadShader('assets/shaders/black_parts.sha')
            floor_shader = loader.loadShader('assets/shaders/floor.sha')
            self.floor.setShader(floor_shader)
            self.walls.setShader(wall_shader)
            self.black.setShader(black_shader)
            self.floor.hide(BitMask32.bit(1))
        if not self.common['safemode']:
            render.setShaderInput("slight0", self.Ambient)
            render.setShaderInput("plight0", self.pLightNode)

            tex = loader.loadTexture('assets/textures/ui/fog2.png')
            self.proj = render.attachNewNode(LensNode('proj'))
            lens = PerspectiveLens()
            lens.setFov(45)
            self.proj.node().setLens(lens)
            self.proj.reparentTo(render)
            self.proj.setHpr(180, 45, 0)
            self.proj.setZ(0.0)
            self.proj.reparentTo(self.cameraNode)
            ts = TextureStage('ts')
            tex.setWrapU(Texture.WMBorderColor)
            tex.setWrapV(Texture.WMBorderColor)
            tex.setBorderColor(Vec4(1, 1, 1, 1))
            self.black.projectTexture(ts, tex, self.proj)
            self.walls.projectTexture(ts, tex, self.proj)

            #shadows
            self.floor.projectTexture(self.common['shadow_ts'], self.common['shadowTexture'], self.common['shadowCamera'])

    def __init__(self, common):
        self.common = common
        self.black = common['map_black']
        self.walls = common['map_walls']
        self.floor = common['map_floor']
        self.monster_list = common['monsterList']
        self.audio3d = common['audio3d']

        if not self.common['safemode']:
            wall_shader = loader.loadShader('assets/shaders/tiles.sha')
            black_shader = loader.loadShader('assets/shaders/black_parts.sha')
            floor_shader = loader.loadShader('assets/shaders/floor.sha')
            self.floor.setShader(floor_shader)
            self.walls.setShader(wall_shader)
            self.black.setShader(black_shader)

            self.floor.hide(BitMask32.bit(1))

        #parent node
        if 'player_node' in common:
            self.node = common['player_node']
        else:
            self.node = render.attachNewNode("pc")

        # Subclass sets up actor
        self._setup_actor()

        self.actor.setBlend(frameBlend=True)
        self.actor.reparentTo(self.node)
        self.actor.setH(180.0)
        self.isIdle = True

        # Subclass sets up sounds (must populate self.sounds dict)
        self.sounds = {}
        self._setup_sounds()

        # Common sounds setup
        self.sounds['walk'].setLoop(True)
        for sound in self.sounds:
            self.audio3d.attachSoundToObject(self.sounds[sound], self.node)

        # Subclass hook for post-sound setup (e.g. extra sounds attached elsewhere)
        self._setup_sounds_extra()

        #camera
        self.cameraNode = render.attachNewNode("cameraNode")
        self.cameraNode.setZ(-1)
        base.camera.setPos(0, -14, 13)
        base.camera.lookAt(self.node)
        base.camera.wrtReparentTo(self.cameraNode)
        self.pointer = self.cameraNode.attachNewNode("pointerNode")
        self.autoCamera = True
        self.pauseCamera = False

        #light
        self.pLight = PointLight('plight')
        self.pLight.setColor(VBase4(.9, .9, 1.0, 1))
        self.pLight.setAttenuation(Point3(2, 0, 0.5))
        self.pLightNode = render.attachNewNode(self.pLight)
        render.setLight(self.pLightNode)

        self.sLight = Spotlight('sLight')
        self.sLight.setColor(VBase4(.5, .45, .45, 1))
        if self.common['extra_ambient']:
            self.sLight.setColor(VBase4(.7, .6, .6, 1))
        spot_lens = PerspectiveLens()
        spot_lens.setFov(160)
        self.sLight.setLens(spot_lens)
        self.Ambient = self.cameraNode.attachNewNode(self.sLight)
        self.Ambient.setPos(base.camera.getPos(render))
        self.Ambient.lookAt(self.node)
        render.setLight(self.Ambient)

        #shaders
        if not self.common['safemode']:
            render.setShaderInput("slight0", self.Ambient)
            render.setShaderInput("plight0", self.pLightNode)

            tex = loader.loadTexture('assets/textures/ui/fog2.png')
            self.proj = render.attachNewNode(LensNode('proj'))
            lens = PerspectiveLens()
            lens.setFov(45)
            self.proj.node().setLens(lens)
            self.proj.reparentTo(render)
            self.proj.setHpr(180, 45, 0)
            self.proj.setZ(0.0)
            self.proj.reparentTo(self.cameraNode)
            ts = TextureStage('ts')
            tex.setWrapU(Texture.WMBorderColor)
            tex.setWrapV(Texture.WMBorderColor)
            tex.setBorderColor(Vec4(1, 1, 1, 1))
            self.black.projectTexture(ts, tex, self.proj)
            self.walls.projectTexture(ts, tex, self.proj)

            #shadows
            self.floor.projectTexture(self.common['shadow_ts'], self.common['shadowTexture'], self.common['shadowCamera'])

        #the plane will by used to see where the mouse pointer is
        self.plane = Plane(Vec3(0, 0, 1), Point3(0, 0, 1))

        #key mapping
        self.keyMap = {'key_forward': False,
                        'key_back': False,
                        'key_left': False,
                        'key_right': False,
                        'key_cam_left': False,
                        'key_cam_right': False,
                        'key_action1': False,
                        'key_action2': False}
        #prime key
        self.accept(common['keymap']['key_forward'][0], self.keyMap.__setitem__, ["key_forward", True])
        self.accept(common['keymap']['key_back'][0], self.keyMap.__setitem__, ["key_back", True])
        self.accept(common['keymap']['key_left'][0], self.keyMap.__setitem__, ["key_left", True])
        self.accept(common['keymap']['key_right'][0], self.keyMap.__setitem__, ["key_right", True])
        self.accept(common['keymap']['key_cam_left'][0], self.keyMap.__setitem__, ["key_cam_left", True])
        self.accept(common['keymap']['key_cam_right'][0], self.keyMap.__setitem__, ["key_cam_right", True])
        self.accept(common['keymap']['key_action1'][0], self.keyMap.__setitem__, ["key_action1", True])
        self.accept(common['keymap']['key_action2'][0], self.keyMap.__setitem__, ["key_action2", True])
        #alt key
        self.accept(common['keymap']['key_forward'][1], self.keyMap.__setitem__, ["key_forward", True])
        self.accept(common['keymap']['key_back'][1], self.keyMap.__setitem__, ["key_back", True])
        self.accept(common['keymap']['key_left'][1], self.keyMap.__setitem__, ["key_left", True])
        self.accept(common['keymap']['key_right'][1], self.keyMap.__setitem__, ["key_right", True])
        self.accept(common['keymap']['key_cam_left'][1], self.keyMap.__setitem__, ["key_cam_left", True])
        self.accept(common['keymap']['key_cam_right'][1], self.keyMap.__setitem__, ["key_cam_right", True])
        self.accept(common['keymap']['key_action1'][1], self.keyMap.__setitem__, ["key_action1", True])
        self.accept(common['keymap']['key_action2'][1], self.keyMap.__setitem__, ["key_action2", True])
        self.accept(common['keymap']['key_forward'][0], self.keyMap.__setitem__, ["key_forward", True])
        #prime key up
        self.accept(common['keymap']['key_forward'][0]+"-up", self.keyMap.__setitem__, ["key_forward", False])
        self.accept(common['keymap']['key_back'][0]+"-up", self.keyMap.__setitem__, ["key_back", False])
        self.accept(common['keymap']['key_left'][0]+"-up", self.keyMap.__setitem__, ["key_left", False])
        self.accept(common['keymap']['key_right'][0]+"-up", self.keyMap.__setitem__, ["key_right", False])
        self.accept(common['keymap']['key_cam_left'][0]+"-up", self.keyMap.__setitem__, ["key_cam_left", False])
        self.accept(common['keymap']['key_cam_right'][0]+"-up", self.keyMap.__setitem__, ["key_cam_right", False])
        self.accept(common['keymap']['key_action1'][0]+"-up", self.keyMap.__setitem__, ["key_action1", False])
        self.accept(common['keymap']['key_action2'][0]+"-up", self.keyMap.__setitem__, ["key_action2", False])
        #alt key up
        self.accept(common['keymap']['key_forward'][1]+"-up", self.keyMap.__setitem__, ["key_forward", False])
        self.accept(common['keymap']['key_back'][1]+"-up", self.keyMap.__setitem__, ["key_back", False])
        self.accept(common['keymap']['key_left'][1]+"-up", self.keyMap.__setitem__, ["key_left", False])
        self.accept(common['keymap']['key_right'][1]+"-up", self.keyMap.__setitem__, ["key_right", False])
        self.accept(common['keymap']['key_cam_left'][1]+"-up", self.keyMap.__setitem__, ["key_cam_left", False])
        self.accept(common['keymap']['key_cam_right'][1]+"-up", self.keyMap.__setitem__, ["key_cam_right", False])
        self.accept(common['keymap']['key_action1'][1]+"-up", self.keyMap.__setitem__, ["key_action1", False])
        self.accept(common['keymap']['key_action2'][1]+"-up", self.keyMap.__setitem__, ["key_action2", False])
        self.accept(common['keymap']['key_forward'][0]+"-up", self.keyMap.__setitem__, ["key_forward", False])

        #camera zoom
        self.accept(common['keymap']['key_zoomin'][0], self.zoom_control, [0.1])
        self.accept(common['keymap']['key_zoomout'][0], self.zoom_control, [-0.1])
        self.accept(common['keymap']['key_zoomin'][1], self.zoom_control, [0.1])
        self.accept(common['keymap']['key_zoomout'][1], self.zoom_control, [-0.1])

        self.lastPos = self.node.getPos(render)
        self.camera_momentum = 1.0
        self.powerUp = 0
        self.actionLock = 0
        self.hitMonsters = set()
        self.myWaypoints = []

        # Subclass sets up stats (HP, MaxHP, speed, damage, etc.)
        self._setup_stats()

        #gui
        wp = base.win.getProperties()
        winX = wp.getXSize()
        winY = wp.getYSize()
        self.cursor = DirectFrame(frameSize=(-32, 0, 0, 32),
                                    frameColor=(1, 1, 1, 1),
                                    frameTexture='assets/icons/cursors/cursor1.png',
                                    parent=pixel2d)
        self.cursor.setPos(32, 0, -32)
        self.cursor.flattenLight()
        self.cursor.setBin('fixed', 10)
        self.cursor.setTransparency(TransparencyAttrib.MDual)

        self.cursorPowerUV = [0.0, 0.75]
        self.cursorPower = DirectFrame(frameSize=(-64, 0, 0, 64),
                                    frameColor=(1, 1, 1, 1),
                                    frameTexture='assets/icons/hud/arc_grow2.png',
                                    parent=self.cursor)
        self.cursorPower.setPos(48, 0, -48)
        self.cursorPower.stateNodePath[0].setTexScale(TextureStage.getDefault(), 0.25, 0.25)
        self.cursorPower.stateNodePath[0].setTexOffset(TextureStage.getDefault(), self.cursorPowerUV[0], self.cursorPowerUV[1])
        self.cursorPower2 = DirectFrame(frameSize=(-64, 0, 0, 64),
                                    frameColor=(1, 1, 1, 1),
                                    frameTexture='assets/icons/hud/arc_shrink.png',
                                    parent=self.cursor)
        self.cursorPowerUV2 = [0.0, 0.75]
        self.cursorPower2.setPos(48, 0, -48)
        self.cursorPower2.stateNodePath[0].setTexScale(TextureStage.getDefault(), 0.25, 0.25)
        self.cursorPower2.stateNodePath[0].setTexOffset(TextureStage.getDefault(), self.cursorPowerUV2[0], self.cursorPowerUV2[1])

        self.healthFrame = DirectFrame(frameSize=(-512, 0, 0, 64),
                                    frameColor=(1, 1, 1, 1),
                                    frameTexture='assets/icons/hud/health_frame2.png',
                                    parent=pixel2d)
        self.healthFrame.setTransparency(TransparencyAttrib.MDual)

        self.healthBar = DirectFrame(frameSize=(37, 0, 0, 16),
                                    frameColor=(0, 1, 0, 1),
                                    frameTexture='assets/icons/hud/glass4.png',
                                    parent=pixel2d)
        self.healthBar.setTransparency(TransparencyAttrib.MDual)
        self.healthBar.setScale(10, 1, 1)
        self.isOptionsOpen = True
        self.options = DirectFrame(frameSize=(-256, 0, 0, 128),
                                    frameColor=(1, 1, 1, 1),
                                    frameTexture='assets/icons/skills/options.png',
                                    parent=pixel2d)
        self.options.setTransparency(TransparencyAttrib.MDual)
        self.options.setPos(winX, 0, -128)
        self.options.setBin('fixed', 1)
        self.options_close = DirectFrame(frameSize=(-32, 0, 0, 32),
                                    frameColor=(1, 1, 1, 0),
                                    state=DGG.NORMAL,
                                    parent=self.options)
        self.options_close.setPos(-221, 0, 5)
        self.options_close.bind(DGG.B1PRESS, self.optionsSet, ['close'])
        self.options_exit = DirectFrame(frameSize=(-200, 0, 0, 40),
                                    frameColor=(1, 1, 1, 0),
                                    state=DGG.NORMAL,
                                    parent=self.options)
        self.options_exit.bind(DGG.B1PRESS, self.optionsSet, ['exit'])
        self.options_slider1 = DirectSlider(range=(0, 100),
                                    value=self.common['soundVolume'],
                                    pageSize=10,
                                    thumb_relief=DGG.FLAT,
                                    thumb_frameTexture='assets/textures/ui/glass3.png',
                                    scale=70,
                                    thumb_frameSize=(0.07, -0.07, -0.11, 0.11),
                                    frameTexture='assets/textures/ui/glass2.png',
                                    command=self.optionsSet,
                                    extraArgs=["audio"],
                                    parent=pixel2d)
        self.options_slider1.setBin('fixed', 2)
        self.options_slider1.setPos(-95+winX, 0, -24)
        self.options_slider1.wrtReparentTo(self.options)

        self.options_slider2 = DirectSlider(range=(0, 100),
                                    value=self.common['musicVolume'],
                                    pageSize=10,
                                    thumb_relief=DGG.FLAT,
                                    thumb_frameTexture='assets/textures/ui/glass3.png',
                                    scale=70,
                                    thumb_frameSize=(0.07, -0.07, -0.11, 0.11),
                                    frameTexture='assets/textures/ui/glass2.png',
                                    command=self.optionsSet,
                                    extraArgs=["music"],
                                    parent=pixel2d)
        self.options_slider2.setBin('fixed', 2)
        self.options_slider2.setPos(-95+winX, 0, -50)
        self.options_slider2.wrtReparentTo(self.options)

        self.options_rew = DirectFrame(frameSize=(-16, 0, 0, 16),
                                    frameColor=(1, 1, 1, 0),
                                    state=DGG.NORMAL,
                                    parent=self.options)
        self.options_rew.setPos(-185, 0, 50)
        self.options_rew.bind(DGG.B1PRESS, self.optionsSet, ['rew'])

        self.options_loop = DirectFrame(frameSize=(-16, 0, 0, 16),
                                    frameColor=(1, 1, 1, 0),
                                    state=DGG.NORMAL,
                                    parent=self.options)
        self.options_loop.setPos(-159, 0, 50)
        self.options_loop.bind(DGG.B1PRESS, self.optionsSet, ['loop'])

        self.options_play = DirectFrame(frameSize=(-16, 0, 0, 16),
                                    frameColor=(1, 1, 1, 0),
                                    state=DGG.NORMAL,
                                    parent=self.options)
        self.options_play.setPos(-140, 0, 50)
        self.options_play.bind(DGG.B1PRESS, self.optionsSet, ['play'])

        self.options_shuffle = DirectFrame(frameSize=(-16, 0, 0, 16),
                                    frameColor=(1, 1, 1, 0),
                                    state=DGG.NORMAL,
                                    parent=self.options)
        self.options_shuffle.setPos(-115, 0, 50)
        self.options_shuffle.bind(DGG.B1PRESS, self.optionsSet, ['shufle'])

        self.options_ff = DirectFrame(frameSize=(-16, 0, 0, 16),
                                    frameColor=(1, 1, 1, 0),
                                    state=DGG.NORMAL,
                                    parent=self.options)
        self.options_ff.setPos(-92, 0, 50)
        self.options_ff.bind(DGG.B1PRESS, self.optionsSet, ['ff'])

        self.options_autocam = DirectFrame(frameSize=(-70, 0, 0, 16),
                                    frameColor=(1, 1, 1, 0),
                                    state=DGG.NORMAL,
                                    parent=self.options)
        self.options_autocam.setPos(-10, 0, 50)
        self.options_autocam.bind(DGG.B1PRESS, self.optionsSet, ['autocam'])

        self.optionsSet("close")

        self.healthFrame.setPos(256+winX/2, 0, -winY)
        self.healthBar.setPos(71-256+winX/2, 0, 7-winY)

        # Subclass-specific init before collisions
        self._setup_pre_collisions()

        #collision ray for testing visibility polygons
        self.coll_ray = self.node.attachNewNode(CollisionNode('collRay'))
        self.coll_ray.node().addSolid(CollisionRay(0, 0, 2, 0, 0, -180))
        self.coll_ray.setTag("visibility", "0")
        self.coll_ray.node().setIntoCollideMask(BitMask32.allOff())
        self.coll_ray.node().setFromCollideMask(BitMask32.bit(1))
        self.common['traverser'].addCollider(self.coll_ray, self.common['queue'])

        #collision sphere
        self.mask_2_3 = BitMask32.bit(3)
        self.mask_2_3.setBit(2)
        self.coll_sphere = self.node.attachNewNode(CollisionNode('playerSphere'))
        self.coll_sphere.node().addSolid(self._get_player_collision_solid())
        self.coll_sphere.setTag("player", "1")
        self.coll_sphere.node().setIntoCollideMask(BitMask32.bit(2))
        self.coll_sphere.node().setFromCollideMask(self.mask_2_3)
        self.common['traverser'].addCollider(self.coll_sphere, self.common['queue'])

        # Subclass sets up extra collisions (attack ray, arrow spheres, etc.)
        self._setup_collisions_extra()

        self.accept('window-event', self.windowEventHandler)
        self.accept("escape", self.optionsSet, ['close'])

        taskMgr.add(self.__getMousePos, "mousePosTask")
        taskMgr.add(self.update, "updatePC")

        # Subclass registers its specific tasks
        self._setup_tasks()

    # --- Hooks for subclasses to override ---

    def _setup_actor(self):
        """Subclass must create self.actor and set scale, play rates, bin, etc."""
        raise NotImplementedError

    def _setup_sounds(self):
        """Subclass must populate self.sounds dict with all sounds."""
        raise NotImplementedError

    def _setup_sounds_extra(self):
        """Hook for extra sound setup after common loop attachment. Override if needed."""
        pass

    def _setup_stats(self):
        """Subclass must set self.HP, self.MaxHP, self.speed, and any class-specific stats."""
        raise NotImplementedError

    def _setup_pre_collisions(self):
        """Hook called after GUI setup but before collision setup. Override if needed."""
        pass

    def _get_player_collision_solid(self):
        """Return the CollisionSphere for the player. Default is (0,0,1, 0.4)."""
        return CollisionSphere(0, 0, 1, 0.4)

    def _setup_collisions_extra(self):
        """Subclass sets up attack rays, arrow spheres, etc."""
        pass

    def _setup_tasks(self):
        """Subclass registers its doMethodLater tasks."""
        raise NotImplementedError

    def _get_task_names(self):
        """Return list of class-specific task name strings for cleanup."""
        return []

    def _destroy_extra(self):
        """Subclass cleans up extra resources (lightning vfx, arrow spheres, etc.)."""
        pass

    def _handle_combat(self, task, dt, anim):
        """Handle class-specific combat logic in update. Return task status or None to continue."""
        return None

    def _handle_collision_entries(self, entry):
        """Process class-specific collision entries. Called for each entry in the queue."""
        pass

    def _update_auto_camera_extra_check(self):
        """Return True if auto camera should be skipped this frame. Default False."""
        return False

    def _update_pre_traverse(self, dt):
        """Called in update before traverser.traverse. Override for class-specific per-frame logic."""
        pass

    def _update_movement_speed(self):
        """Return (forward_speed, back_speed, strafe_speed, walk_rate, back_rate).
        Default values match PC2/PC3 (no speed modifier)."""
        return (4, 3, 4, 1, -0.8)

    # --- Common methods ---

    def optionsSet(self, opt, event=None):
        if opt != "close" and opt != "audio" and opt != "music":
            self.common['click'].play()
        if opt == "close":
            wp = base.win.getProperties()
            winX = wp.getXSize()
            if self.isOptionsOpen:
                Sequence(LerpPosInterval(self.options, 0.1, VBase3(winX, 0, -128+84)), LerpPosInterval(self.options, 0.2, VBase3(210+winX, 0, -128+84))).start()
                self.isOptionsOpen = False
                self.options_exit.hide()
                self.options_slider1.hide()
                self.options_slider2.hide()
                self.options_rew.hide()
                self.options_loop.hide()
                self.options_play.hide()
                self.options_shuffle.hide()
                self.options_ff.hide()
                self.options_autocam.hide()
            else:
                Sequence(LerpPosInterval(self.options, 0.2, VBase3(winX, 0, -128+84)), LerpPosInterval(self.options, 0.1, VBase3(winX, 0, -128))).start()
                self.isOptionsOpen = True
                self.options_exit.show()
                self.options_slider1.show()
                self.options_slider2.show()
                self.options_rew.show()
                self.options_loop.show()
                self.options_play.show()
                self.options_shuffle.show()
                self.options_ff.show()
                self.options_autocam.show()
        elif opt == "exit":
            self.destroy()
        elif opt == "audio":
            base.sfxManagerList[0].setVolume(self.options_slider1['value']*0.01)
        elif opt == "music":
            self.common['music'].setVolume(self.options_slider2['value'])
        elif opt == "rew":
            self.common['music'].REW()
        elif opt == "loop":
            self.common['music'].setLoop(True)
        elif opt == "play":
            self.common['music'].setLoop(False)
        elif opt == "shufle":
            self.common['music'].setShuffle()
        elif opt == "ff":
            self.common['music'].FF()
        elif opt == "autocam":
            if self.autoCamera:
                self.autoCamera = False
            else:
                self.autoCamera = True

    def heal(self):
        self.sounds["heal"].play()
        vfx(self.node, texture='vfx/vfx3.png', scale=.8, Z=1.0, depthTest=False, depthWrite=False).start(0.03)
        self.healthBar.setScale(10, 1, 1)
        self.healthBar['frameColor'] = (0, 1, 0, 1)
        self.HP = self.MaxHP

    def zoom(self, t):
        Z = base.camera.getY(self.cameraNode)
        if Z >= -5 and t > 0:
            t = 0
        elif Z <= -16 and t < 0:
            t = 0
        base.camera.setY(base.camera, t)
        base.camera.setZ(base.camera, -t/2.5)
        base.camera.setP(base.camera, t*2.0)

    def zoom_control(self, amount):
        LerpFunc(self.zoom, fromData=0, toData=amount, duration=.5, blendType='easeOut').start()

    def update(self, task):
        dt = globalClock.getDt()
        self.cameraNode.setPos(self.node.getPos(render))

        # Per-frame pre-traverse logic (subclass hook)
        self._update_pre_traverse(dt)

        #auto camera
        if not self._update_auto_camera_extra_check():
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
                    t = dt*delta/2
                    if t > .020:
                        t = .020
                    t = min(t, 1.0)
                    newHpr = origHpr + (targetHpr - origHpr) * t
                    self.cameraNode.setHpr(newHpr)
                    self.camera_momentum += dt*3

        if self.camera_momentum > 3.0:
            self.camera_momentum = 3.0
        #rotate camera
        if self.keyMap["key_cam_right"]:
            self.cameraNode.setH(self.cameraNode, -35*dt*self.camera_momentum)
            self.camera_momentum += dt*1.5
        elif self.keyMap["key_cam_left"]:
            self.cameraNode.setH(self.cameraNode, 35*dt*self.camera_momentum)
            self.camera_momentum += dt*1.5
        else:
            self.camera_momentum = max(0, self.camera_momentum - dt*6.0)

        if self.HP <= 0:
            return task.again

        self.common['traverser'].traverse(render)
        hit_wall = False
        self.myWaypoints = []

        for entry in self.common['queue'].getEntries():
            if entry.getFromNodePath().hasTag("player"):
                hit_wall = True
                if entry.getIntoNodePath().hasTag("id"):
                    self.monster_list[int(entry.getIntoNodePath().getTag("id"))].PCisInRange = True
                    hit_wall = False
            if entry.getFromNodePath().hasTag("attack"):
                self.hitMonsters.add(entry.getIntoNodePath().getTag("id"))
            if entry.getIntoNodePath().hasTag("index"):
                self.myWaypoints.append(int(entry.getIntoNodePath().getTag("index")))
            # Subclass-specific collision handling
            self._handle_collision_entries(entry)

        if hit_wall:
            self.node.setPos(self.lastPos)

        # Class-specific combat handling
        anim = self.actor.getCurrentAnim()
        combat_result = self._handle_combat(task, dt, anim)
        if combat_result is not None:
            return combat_result

        #move
        self.lastPos = self.node.getPos(render)
        fwd_speed, back_speed, strafe_speed, walk_rate, back_rate = self._update_movement_speed()

        if self.keyMap["key_forward"]:
            self.isIdle = False
            self.node.setFluidY(self.node, dt*fwd_speed)
            self.actor.setPlayRate(walk_rate, "walk")
            if self.actor.getCurrentAnim() != "walk":
                self.actor.loop("walk")
                if self.sounds["walk"].status() != self.sounds["walk"].PLAYING:
                    self.sounds["walk"].play()
            if self.keyMap["key_right"]:
                self.node.setFluidX(self.node, dt*1)
            if self.keyMap["key_left"]:
                self.node.setFluidX(self.node, -dt*1)
        elif self.keyMap["key_right"]:
            self.isIdle = False
            self.node.setFluidX(self.node, dt*strafe_speed)
            self.actor.setPlayRate(-2, "strafe")
            if self.actor.getCurrentAnim() != "strafe":
                self.actor.loop("strafe")
        elif self.keyMap["key_left"]:
            self.isIdle = False
            self.node.setFluidX(self.node, -dt*strafe_speed)
            self.actor.setPlayRate(2, "strafe")
            if self.actor.getCurrentAnim() != "strafe":
                self.actor.loop("strafe")
        elif self.keyMap["key_back"]:
            self.isIdle = False
            self.node.setFluidY(self.node, -dt*back_speed)
            self.actor.setPlayRate(back_rate, "walk")
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

    def __getMousePos(self, task):
        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()
            pos3d = Point3()
            nearPoint = Point3()
            farPoint = Point3()
            base.camLens.extrude(mpos, nearPoint, farPoint)
            if self.plane.intersectsLine(pos3d, render.getRelativePoint(camera, nearPoint), render.getRelativePoint(camera, farPoint)):
                self._on_mouse_pos3d(pos3d)
                if self.HP > 0:
                    self.node.headsUp(pos3d)
                self.pLightNode.setPos(pos3d)
                self.pLightNode.setZ(2.7)
                if not self.common['safemode']:
                    if self.node.getDistance(self.pLightNode) < 13.0:
                        self.common['shadowNode'].setPos(self.pLightNode.getPos(render))
                        self.common['shadowNode'].setZ(2.7)
            pos2d = Point3(base.mouseWatcherNode.getMouseX(), 0, base.mouseWatcherNode.getMouseY())
            self.cursor.setPos(pixel2d.getRelativePoint(render2d, pos2d))
        return task.again

    def _on_mouse_pos3d(self, pos3d):
        """Hook called when mouse pos3d is computed. Override for class-specific behavior."""
        pass

    def windowEventHandler(self, window=None):
        if window is not None:
            wp = base.win.getProperties()
            winX = wp.getXSize()
            winY = wp.getYSize()
            self.healthFrame.setPos(256+winX/2, 0, -winY)
            self.healthBar.setPos(71-256+winX/2, 0, 7-winY)
            if self.isOptionsOpen:
                self.options.setPos(winX, 0, -128)
            else:
                self.options.setPos(210+winX, 0, -128+84)

    def destroy(self):
        self.common['levelLoader'].unload(True)

        # Subclass-specific cleanup first
        self._destroy_extra()

        if taskMgr.hasTaskNamed("mousePosTask"):
            taskMgr.remove("mousePosTask")
        if taskMgr.hasTaskNamed("updatePC"):
            taskMgr.remove("updatePC")
        for task_name in self._get_task_names():
            if taskMgr.hasTaskNamed(task_name):
                taskMgr.remove(task_name)

        self.healthFrame.destroy()
        self.healthBar.destroy()
        self.cursor.destroy()
        self.cursorPower.destroy()
        self.cursorPower2.destroy()
        self.options.destroy()
        self.options_close.destroy()
        self.options_exit.destroy()
        self.options_slider1.destroy()
        self.options_slider2.destroy()

        self.actor.cleanup()
        render.setLightOff()
        self.ignoreAll()

        self.actor.removeNode()
        self.pLightNode.removeNode()
        self.Ambient.removeNode()

        self.cameraNode.removeNode()
        base.camera.reparentTo(render)

        self.keyMap = None
        self.lastPos = None
        self.camera_momentum = None
        self.powerUp = None
        self.actionLock = None
        self.hitMonsters = None
        self.myWaypoints = None
        self.HP = None
        self.cursorPowerUV = None
        self.cursorPowerUV2 = None

        self.common['traverser'].removeCollider(self.coll_ray)
        self.common['traverser'].removeCollider(self.coll_sphere)

        self.coll_ray.removeNode()
        self.coll_sphere.removeNode()
        self.node.setPos(0, 0, 0)
        self.common['player_node'] = self.node
        self.common['CharGen'].load()
