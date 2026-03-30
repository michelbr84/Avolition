"""
Sistema de Partículas Moderno para Avolition
Efeitos visuais avançados com física realista
"""

import random
import math
from panda3d.core import Point3, Vec3, Vec4, NodePath, PandaNode
from panda3d.core import GeomNode, Geom, GeomVertexData, GeomVertexFormat
from panda3d.core import GeomVertexWriter, GeomTriangles, GeomNode
from panda3d.core import TransparencyAttrib, AntialiasAttrib
from panda3d.core import Texture, TextureStage, Shader, ShaderAttrib
import numpy as np

class Particle:
    def __init__(self, position, velocity, color, size, life):
        self.position = Vec3(position)
        self.velocity = Vec3(velocity)
        self.color = Vec4(color)
        self.size = size
        self.life = life
        self.max_life = life
        self.gravity = Vec3(0, -9.81, 0)
        self.drag = 0.98
        
    def update(self, dt):
        """Atualiza a partícula com física"""
        self.velocity += self.gravity * dt
        self.velocity *= self.drag
        self.position += self.velocity * dt
        self.life -= dt
        
        # Atualiza alpha baseado na vida
        alpha = self.life / self.max_life
        self.color.w = alpha
        
        return self.life > 0

class ParticleSystem:
    def __init__(self, max_particles=1000):
        self.particles = []
        self.max_particles = max_particles
        self.node = NodePath(PandaNode("particle_system"))
        self.geom_node = None
        self.texture = None
        self._setup_geometry()
        self._setup_shader()
    
    def _setup_geometry(self):
        """Configura a geometria das partículas"""
        format = GeomVertexFormat.getV3c4t2()
        vdata = GeomVertexData('particles', format, Geom.UHStatic)
        
        vertex = GeomVertexWriter(vdata, 'vertex')
        color = GeomVertexWriter(vdata, 'color')
        texcoord = GeomVertexWriter(vdata, 'texcoord')
        
        # Cria um quad para cada partícula (billboard)
        for i in range(self.max_particles):
            # Vértices do quad
            vertex.addData3(-0.5, -0.5, 0)
            vertex.addData3(0.5, -0.5, 0)
            vertex.addData3(0.5, 0.5, 0)
            vertex.addData3(-0.5, 0.5, 0)
            
            # Cores (serão atualizadas dinamicamente)
            for _ in range(4):
                color.addData4(1, 1, 1, 1)
            
            # Coordenadas de textura
            texcoord.addData2(0, 0)
            texcoord.addData2(1, 0)
            texcoord.addData2(1, 1)
            texcoord.addData2(0, 1)
        
        # Cria os triângulos
        tris = GeomTriangles(Geom.UHStatic)
        for i in range(self.max_particles):
            base = i * 4
            tris.addVertices(base, base + 1, base + 2)
            tris.addVertices(base, base + 2, base + 3)
        
        geom = Geom(vdata)
        geom.addPrimitive(tris)
        
        self.geom_node = GeomNode('particle_geom')
        self.geom_node.addGeom(geom)
        self.node.attachNewNode(self.geom_node)
        
        # Configura atributos de renderização
        self.node.setTransparency(TransparencyAttrib.MAlpha)
        self.node.setAntialias(AntialiasAttrib.MPoint)
    
    def _setup_shader(self):
        """Configura o shader para as partículas"""
        vertex_shader = """
        #version 330
        uniform mat4 p3d_ModelViewProjectionMatrix;
        uniform mat4 p3d_ModelViewMatrix;
        uniform vec3 cameraPos;
        
        in vec3 p3d_Vertex;
        in vec4 p3d_Color;
        in vec2 p3d_MultiTexCoord0;
        
        out vec4 color;
        out vec2 texCoord;
        
        void main() {
            // Billboard: sempre olha para a câmera
            vec3 pos = p3d_Vertex;
            vec3 toCamera = normalize(cameraPos - pos);
            vec3 right = normalize(cross(toCamera, vec3(0, 1, 0)));
            vec3 up = normalize(cross(right, toCamera));
            
            pos += right * p3d_Vertex.x + up * p3d_Vertex.y;
            
            gl_Position = p3d_ModelViewProjectionMatrix * vec4(pos, 1.0);
            color = p3d_Color;
            texCoord = p3d_MultiTexCoord0;
        }
        """
        
        fragment_shader = """
        #version 330
        uniform sampler2D particleTexture;
        
        in vec4 color;
        in vec2 texCoord;
        
        out vec4 fragColor;
        
        void main() {
            vec4 texColor = texture(particleTexture, texCoord);
            fragColor = color * texColor;
            
            // Soft particles: suaviza as bordas
            float dist = length(texCoord - vec2(0.5));
            if (dist > 0.5) {
                fragColor.a *= 1.0 - smoothstep(0.5, 0.6, dist);
            }
        }
        """
        
        shader = Shader.make(Shader.SL_GLSL, vertex_shader, fragment_shader)
        shader_attrib = ShaderAttrib.make(shader)
        self.node.setShaderAttrib(shader_attrib)
    
    def set_texture(self, texture_path):
        """Define a textura das partículas"""
        self.texture = loader.loadTexture(texture_path)
        if self.texture:
            self.node.setTexture(self.texture)
    
    def emit_fire(self, position, count=20):
        """Emite partículas de fogo"""
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break
                
            # Velocidade aleatória para cima
            vel = Vec3(
                random.uniform(-2, 2),
                random.uniform(3, 8),
                random.uniform(-2, 2)
            )
            
            # Cor do fogo (laranja para vermelho)
            color = Vec4(
                random.uniform(0.8, 1.0),
                random.uniform(0.3, 0.6),
                random.uniform(0.0, 0.2),
                1.0
            )
            
            particle = Particle(
                position,
                vel,
                color,
                random.uniform(0.5, 2.0),
                random.uniform(1.0, 3.0)
            )
            self.particles.append(particle)
    
    def emit_explosion(self, position, count=50):
        """Emite partículas de explosão"""
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break
                
            # Velocidade em todas as direções
            angle = random.uniform(0, 2 * math.pi)
            elevation = random.uniform(-math.pi/2, math.pi/2)
            speed = random.uniform(5, 15)
            
            vel = Vec3(
                speed * math.cos(elevation) * math.cos(angle),
                speed * math.sin(elevation),
                speed * math.cos(elevation) * math.sin(angle)
            )
            
            # Cor da explosão (amarelo para laranja)
            color = Vec4(
                random.uniform(0.8, 1.0),
                random.uniform(0.6, 0.9),
                random.uniform(0.0, 0.3),
                1.0
            )
            
            particle = Particle(
                position,
                vel,
                color,
                random.uniform(1.0, 4.0),
                random.uniform(0.5, 2.0)
            )
            self.particles.append(particle)
    
    def emit_magic(self, position, count=30):
        """Emite partículas mágicas"""
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break
                
            # Movimento espiral
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(0.5, 2.0)
            speed = random.uniform(1, 3)
            
            vel = Vec3(
                radius * math.cos(angle) * speed,
                random.uniform(1, 4),
                radius * math.sin(angle) * speed
            )
            
            # Cor mágica (azul/roxo)
            color = Vec4(
                random.uniform(0.3, 0.7),
                random.uniform(0.5, 0.8),
                random.uniform(0.8, 1.0),
                1.0
            )
            
            particle = Particle(
                position,
                vel,
                color,
                random.uniform(0.3, 1.5),
                random.uniform(2.0, 5.0)
            )
            self.particles.append(particle)
    
    def emit_blood(self, position, direction, count=15):
        """Emite partículas de sangue"""
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break
                
            # Velocidade baseada na direção do golpe
            vel = direction * random.uniform(2, 8)
            vel += Vec3(
                random.uniform(-3, 3),
                random.uniform(-2, 2),
                random.uniform(-3, 3)
            )
            
            # Cor do sangue
            color = Vec4(
                random.uniform(0.6, 0.9),
                random.uniform(0.0, 0.2),
                random.uniform(0.0, 0.2),
                1.0
            )
            
            particle = Particle(
                position,
                vel,
                color,
                random.uniform(0.5, 2.0),
                random.uniform(1.0, 3.0)
            )
            self.particles.append(particle)
    
    def update(self, dt):
        """Atualiza todas as partículas"""
        # Remove partículas mortas
        self.particles = [p for p in self.particles if p.update(dt)]
        
        # Atualiza a geometria
        self._update_geometry()
    
    def _update_geometry(self):
        """Atualiza a geometria com as posições das partículas"""
        if not self.geom_node:
            return
            
        geom = self.geom_node.getGeom(0)
        vdata = geom.modifyVertex(0)
        
        vertex = GeomVertexWriter(vdata, 'vertex')
        color = GeomVertexWriter(vdata, 'color')
        
        # Atualiza cada partícula
        for i, particle in enumerate(self.particles):
            base = i * 4
            
            # Posições dos vértices do quad
            size = particle.size
            pos = particle.position
            
            vertex.setRow(base)
            vertex.setData3(pos.x - size/2, pos.y - size/2, pos.z)
            vertex.setRow(base + 1)
            vertex.setData3(pos.x + size/2, pos.y - size/2, pos.z)
            vertex.setRow(base + 2)
            vertex.setData3(pos.x + size/2, pos.y + size/2, pos.z)
            vertex.setRow(base + 3)
            vertex.setData3(pos.x - size/2, pos.y + size/2, pos.z)
            
            # Cores
            for j in range(4):
                color.setRow(base + j)
                color.setData4(particle.color)
        
        # Limpa partículas não utilizadas
        for i in range(len(self.particles), self.max_particles):
            base = i * 4
            for j in range(4):
                color.setRow(base + j)
                color.setData4(0, 0, 0, 0)

class ParticleManager:
    def __init__(self):
        self.systems = {}
    
    def create_system(self, name, max_particles=1000):
        """Cria um novo sistema de partículas"""
        system = ParticleSystem(max_particles)
        self.systems[name] = system
        return system
    
    def get_system(self, name):
        """Obtém um sistema de partículas"""
        return self.systems.get(name)
    
    def update_all(self, dt):
        """Atualiza todos os sistemas"""
        for system in self.systems.values():
            system.update(dt)
    
    def cleanup(self):
        """Remove sistemas vazios"""
        empty_systems = [name for name, system in self.systems.items() 
                        if len(system.particles) == 0]
        for name in empty_systems:
            del self.systems[name]

# Instância global do gerenciador de partículas
particle_manager = ParticleManager()
