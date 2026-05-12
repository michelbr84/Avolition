"""
Sistema de Shaders Modernos para Avolition
Inclui PBR, iluminação avançada e efeitos visuais modernos
"""

from panda3d.core import Shader, ShaderAttrib, Texture, TextureStage
from panda3d.core import Material, MaterialAttrib, TransparencyAttrib
from panda3d.core import Vec4, Vec3, Point3
import numpy as np

class ModernShaderManager:
    def __init__(self):
        self.shaders = {}
        self.materials = {}
        self._load_shaders()
    
    def _load_shaders(self):
        """Carrega todos os shaders modernos"""
        self._load_pbr_shader()
        self._load_bloom_shader()
        self._load_ssao_shader()
        self._load_motion_blur_shader()
        self._load_water_shader()
    
    def _load_pbr_shader(self):
        """Shader PBR (Physically Based Rendering)"""
        vertex_shader = """
        #version 330
        uniform mat4 p3d_ModelViewProjectionMatrix;
        uniform mat4 p3d_ModelMatrix;
        uniform mat3 p3d_NormalMatrix;
        
        in vec4 p3d_Vertex;
        in vec3 p3d_Normal;
        in vec2 p3d_MultiTexCoord0;
        in vec2 p3d_MultiTexCoord1;
        
        out vec3 worldPos;
        out vec3 normal;
        out vec2 texCoord;
        out vec2 lightmapCoord;
        
        void main() {
            gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
            worldPos = (p3d_ModelMatrix * p3d_Vertex).xyz;
            normal = normalize(p3d_NormalMatrix * p3d_Normal);
            texCoord = p3d_MultiTexCoord0;
            lightmapCoord = p3d_MultiTexCoord1;
        }
        """
        
        fragment_shader = """
        #version 330
        uniform sampler2D albedoMap;
        uniform sampler2D normalMap;
        uniform sampler2D metallicRoughnessMap;
        uniform sampler2D aoMap;
        uniform sampler2D lightmap;
        
        uniform vec3 lightPos;
        uniform vec3 lightColor;
        uniform vec3 viewPos;
        
        in vec3 worldPos;
        in vec3 normal;
        in vec2 texCoord;
        in vec2 lightmapCoord;
        
        out vec4 fragColor;
        
        const float PI = 3.14159265359;
        
        vec3 getNormalFromMap() {
            vec3 tangentNormal = texture(normalMap, texCoord).xyz * 2.0 - 1.0;
            
            vec3 Q1  = dFdx(worldPos);
            vec3 Q2  = dFdy(worldPos);
            vec2 st1 = dFdx(texCoord);
            vec2 st2 = dFdy(texCoord);
            
            vec3 N   = normalize(normal);
            vec3 T  = normalize(Q1*st2.t - Q2*st1.t);
            vec3 B  = -normalize(cross(N, T));
            mat3 TBN = mat3(T, B, N);
            
            return normalize(TBN * tangentNormal);
        }
        
        float DistributionGGX(vec3 N, vec3 H, float roughness) {
            float a = roughness*roughness;
            float a2 = a*a;
            float NdotH = max(dot(N, H), 0.0);
            float NdotH2 = NdotH*NdotH;
            
            float nom   = a2;
            float denom = (NdotH2 * (a2 - 1.0) + 1.0);
            denom = PI * denom * denom;
            
            return nom / denom;
        }
        
        float GeometrySchlickGGX(float NdotV, float roughness) {
            float r = (roughness + 1.0);
            float k = (r*r) / 8.0;
            
            float nom   = NdotV;
            float denom = NdotV * (1.0 - k) + k;
            
            return nom / denom;
        }
        
        float GeometrySmith(vec3 N, vec3 V, vec3 L, float roughness) {
            float NdotV = max(dot(N, V), 0.0);
            float NdotL = max(dot(N, L), 0.0);
            float ggx2 = GeometrySchlickGGX(NdotV, roughness);
            float ggx1 = GeometrySchlickGGX(NdotL, roughness);
            
            return ggx1 * ggx2;
        }
        
        vec3 fresnelSchlick(float cosTheta, vec3 F0) {
            return F0 + (1.0 - F0) * pow(clamp(1.0 - cosTheta, 0.0, 1.0), 5.0);
        }
        
        void main() {
            vec4 albedo = texture(albedoMap, texCoord);
            float metallic = texture(metallicRoughnessMap, texCoord).b;
            float roughness = texture(metallicRoughnessMap, texCoord).g;
            float ao = texture(aoMap, texCoord).r;
            
            vec3 N = getNormalFromMap();
            vec3 V = normalize(viewPos - worldPos);
            vec3 L = normalize(lightPos - worldPos);
            vec3 H = normalize(V + L);
            
            vec3 F0 = vec3(0.04);
            F0 = mix(F0, albedo.rgb, metallic);
            
            // Cook-Torrance BRDF
            float NDF = DistributionGGX(N, H, roughness);
            float G   = GeometrySmith(N, V, L, roughness);
            vec3 F    = fresnelSchlick(max(dot(H, V), 0.0), F0);
            
            vec3 numerator    = NDF * G * F;
            float denominator = 4.0 * max(dot(N, V), 0.0) * max(dot(N, L), 0.0) + 0.0001;
            vec3 specular = numerator / denominator;
            
            vec3 kS = F;
            vec3 kD = vec3(1.0) - kS;
            kD *= 1.0 - metallic;
            
            float NdotL = max(dot(N, L), 0.0);
            
            vec3 Lo = (kD * albedo.rgb / PI + specular) * lightColor * NdotL;
            
            // Ambient lighting
            vec3 ambient = vec3(0.03) * albedo.rgb * ao;
            
            vec3 color = ambient + Lo;
            
            // HDR tonemapping
            color = color / (color + vec3(1.0));
            // gamma correction
            color = pow(color, vec3(1.0/2.2));
            
            fragColor = vec4(color, albedo.a);
        }
        """
        
        self.shaders['pbr'] = Shader.make(Shader.SL_GLSL, vertex_shader, fragment_shader)
    
    def _load_bloom_shader(self):
        """Shader para efeito Bloom"""
        vertex_shader = """
        #version 330
        uniform mat4 p3d_ModelViewProjectionMatrix;
        in vec4 p3d_Vertex;
        in vec2 p3d_MultiTexCoord0;
        out vec2 texCoord;
        
        void main() {
            gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
            texCoord = p3d_MultiTexCoord0;
        }
        """
        
        fragment_shader = """
        #version 330
        uniform sampler2D tex;
        uniform float threshold;
        uniform float intensity;
        
        in vec2 texCoord;
        out vec4 fragColor;
        
        void main() {
            vec4 color = texture(tex, texCoord);
            float brightness = dot(color.rgb, vec3(0.2126, 0.7152, 0.0722));
            
            if(brightness > threshold) {
                fragColor = color * intensity;
            } else {
                fragColor = vec4(0.0, 0.0, 0.0, 1.0);
            }
        }
        """
        
        self.shaders['bloom'] = Shader.make(Shader.SL_GLSL, vertex_shader, fragment_shader)
    
    def _load_ssao_shader(self):
        """Shader para SSAO (Screen Space Ambient Occlusion)"""
        # Implementação simplificada do SSAO
        pass
    
    def _load_motion_blur_shader(self):
        """Shader para Motion Blur"""
        # Implementação do Motion Blur
        pass
    
    def _load_water_shader(self):
        """Shader para água com reflexões e refrações"""
        vertex_shader = """
        #version 330
        uniform mat4 p3d_ModelViewProjectionMatrix;
        uniform mat4 p3d_ModelMatrix;
        uniform float time;
        
        in vec4 p3d_Vertex;
        in vec3 p3d_Normal;
        in vec2 p3d_MultiTexCoord0;
        
        out vec3 worldPos;
        out vec3 normal;
        out vec2 texCoord;
        
        void main() {
            vec4 vertex = p3d_Vertex;
            // Adiciona movimento de onda
            vertex.y += sin(vertex.x * 0.1 + time) * 0.1;
            vertex.y += cos(vertex.z * 0.1 + time * 0.5) * 0.1;
            
            gl_Position = p3d_ModelViewProjectionMatrix * vertex;
            worldPos = (p3d_ModelMatrix * vertex).xyz;
            normal = normalize(p3d_Normal);
            texCoord = p3d_MultiTexCoord0;
        }
        """
        
        fragment_shader = """
        #version 330
        uniform sampler2D waterTexture;
        uniform sampler2D reflectionTexture;
        uniform float time;
        
        in vec3 worldPos;
        in vec3 normal;
        in vec2 texCoord;
        
        out vec4 fragColor;
        
        void main() {
            vec4 waterColor = texture(waterTexture, texCoord + vec2(time * 0.01, 0.0));
            vec4 reflection = texture(reflectionTexture, texCoord);
            
            float fresnel = pow(1.0 - max(dot(normal, vec3(0.0, 1.0, 0.0)), 0.0), 3.0);
            
            fragColor = mix(waterColor, reflection, fresnel * 0.7);
            fragColor.a = 0.8;
        }
        """
        
        self.shaders['water'] = Shader.make(Shader.SL_GLSL, vertex_shader, fragment_shader)
    
    def apply_pbr_material(self, node, albedo_tex, normal_tex, metallic_roughness_tex, ao_tex):
        """Aplica material PBR a um nó"""
        if 'pbr' not in self.shaders:
            return
        
        shader_attrib = ShaderAttrib.make(self.shaders['pbr'])
        
        # Configura as texturas
        if albedo_tex:
            shader_attrib = shader_attrib.setShaderInput('albedoMap', albedo_tex)
        if normal_tex:
            shader_attrib = shader_attrib.setShaderInput('normalMap', normal_tex)
        if metallic_roughness_tex:
            shader_attrib = shader_attrib.setShaderInput('metallicRoughnessMap', metallic_roughness_tex)
        if ao_tex:
            shader_attrib = shader_attrib.setShaderInput('aoMap', ao_tex)
        
        node.setShaderAttrib(shader_attrib)
    
    def apply_water_shader(self, node, water_tex, reflection_tex):
        """Aplica shader de água a um nó"""
        if 'water' not in self.shaders:
            return
        
        shader_attrib = ShaderAttrib.make(self.shaders['water'])
        
        if water_tex:
            shader_attrib = shader_attrib.setShaderInput('waterTexture', water_tex)
        if reflection_tex:
            shader_attrib = shader_attrib.setShaderInput('reflectionTexture', reflection_tex)
        
        shader_attrib = shader_attrib.setShaderInput('time', 0.0)  # Será atualizado no loop principal
        
        node.setShaderAttrib(shader_attrib)
        node.setTransparency(TransparencyAttrib.MAlpha)

# Instância global do gerenciador de shaders
shader_manager = ModernShaderManager()
