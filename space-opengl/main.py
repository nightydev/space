import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import os
import math

# Inicializar Pygame
pygame.init()
pygame.mouse.set_visible(True)

# Configuración de la ventana
width, height = 800, 600
pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
pygame.display.set_caption("OpenGL con Pygame")

# Configuración inicial de OpenGL
glViewport(0, 0, width, height)
glEnable(GL_DEPTH_TEST)
glEnable(GL_TEXTURE_2D)
glEnable(GL_LIGHTING)
glEnable(GL_LIGHT0)
glEnable(GL_COLOR_MATERIAL)
glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
glClearColor(0.0, 0.0, 0.0, 1.0)  # Color de fondo negro

# Variables para el tiempo y la simulación
simulation_time = 0
time_scale = 0.1  # Velocidad de la simulación: 0.5 = medio "año" por segundo

# Configuración de iluminación para el sol
def set_sun_light():
    # Posición de la luz (en el centro donde estará el sol)
    light_position = [0.0, 0.0, 0.0, 1.0]
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    
    # Colores de la luz
    ambient_light = [0.2, 0.2, 0.2, 1.0]  # Luz ambiental baja
    diffuse_light = [1.0, 0.9, 0.7, 1.0]  # Color amarillento
    specular_light = [1.0, 1.0, 0.9, 1.0] # Brillo blanquecino
    
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient_light)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse_light)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular_light)
    
    # Parámetros de atenuación para simular que la luz se desvanece con la distancia
    # Atenuación constante, lineal y cuadrática
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.5)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
    glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.001)

# Función para dibujar la órbita de un planeta
def draw_orbit(radius, segments=100):
    glDisable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)
    
    glColor4f(0.5, 0.5, 0.5, 0.3)  # Color gris semitransparente
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Dibuja un círculo para la órbita
    glBegin(GL_LINE_LOOP)
    for i in range(segments):
        angle = 2.0 * math.pi * i / segments
        x = radius * math.cos(angle)
        z = radius * math.sin(angle)
        glVertex3f(x, 0.0, z)
    glEnd()
    
    glDisable(GL_BLEND)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_LIGHTING)
    glColor4f(1.0, 1.0, 1.0, 1.0)  # Restaurar color

# Función para dibujar anillos (para Saturno y Urano)
def draw_rings(texture, inner_radius, outer_radius, segments=100):
    glBindTexture(GL_TEXTURE_2D, texture)
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Los anillos están en el plano X-Z
    glBegin(GL_QUAD_STRIP)
    for i in range(segments + 1):
        angle = 2.0 * math.pi * i / segments
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)
        
        # Punto exterior del anillo
        glTexCoord2f(0.0, i / segments)
        glVertex3f(outer_radius * cos_angle, 0, outer_radius * sin_angle)
        
        # Punto interior del anillo
        glTexCoord2f(1.0, i / segments)
        glVertex3f(inner_radius * cos_angle, 0, inner_radius * sin_angle)
    glEnd()
    
    glDisable(GL_BLEND)

# Función simple para mostrar información (eliminar overlays problemáticos)
def show_planet_info(planet_name):
    if planet_name:
        print(f"Enfocando: {planet_name}")
    else:
        print("Modo cámara libre")

# Función para dibujar un planeta
def draw_planet(texture, radius, distance, orbit_period, rotation_period, tilt, time):
    glPushMatrix()
    
    # Calcular posición orbital - a menor periodo orbital, más rápido se mueve
    # time / orbit_period da el número de órbitas completadas
    orbit_angle = (time / orbit_period) * 360.0  # grados
    x = distance * math.cos(math.radians(orbit_angle))
    z = distance * math.sin(math.radians(orbit_angle))
    
    # Dibujar órbita
    draw_orbit(distance)
    
    # Posicionar el planeta
    glTranslatef(x, 0.0, z)
    
    # Inclinación del planeta
    glRotatef(tilt, 0.0, 0.0, 1.0)
    
    # Rotación del planeta sobre su eje
    # Aplicamos un factor de desaceleración para la rotación
    # para que sea visualmente más agradable
    rotation_slowdown = 30.0  # Factor de ralentización para la rotación
    days_passed = time * 365.0 / rotation_slowdown
    planet_rotation = (days_passed / rotation_period) * 360.0
    
    # Invertir dirección para planetas con rotación retrógrada (Venus, Urano)
    if rotation_period < 0:
        planet_rotation = -planet_rotation
        rotation_period = -rotation_period
    
    glRotatef(planet_rotation, 0.0, 1.0, 0.0)
    
    # Aplicar textura y dibujar la esfera
    glBindTexture(GL_TEXTURE_2D, texture)
    gluSphere(planet_sphere, radius, 32, 32)
    
    # Devolver la posición para posibles lunas
    pos = (x, 0.0, z)
    
    glPopMatrix()
    return pos

# Función para dibujar una luna
def draw_moon(texture, planet_pos, radius, distance, orbit_period, rotation_period, time):
    glPushMatrix()
    
    # Posicionar en la ubicación del planeta padre
    glTranslatef(planet_pos[0], planet_pos[1], planet_pos[2])
    
    # Convertir el tiempo a días para el cálculo de la órbita lunar
    days_passed = time * 365.0
    
    # Calcular posición orbital alrededor del planeta (orbit_period en días)
    # Aplicamos el mismo factor de desaceleración para la rotación de la luna
    rotation_slowdown = 30.0
    days_passed = days_passed / rotation_slowdown
    orbit_angle = (days_passed / orbit_period) * 360.0
    moon_x = distance * math.cos(math.radians(orbit_angle))
    moon_z = distance * math.sin(math.radians(orbit_angle))
    
    # Dibujar órbita alrededor del planeta
    draw_orbit(distance)
    
    # Posicionar la luna
    glTranslatef(moon_x, 0.0, moon_z)
    
    # Rotación de la luna sobre su eje (rotation_period en días)
    # Ya tenemos days_passed ajustado con el factor de desaceleración
    moon_rotation = (days_passed / rotation_period) * 360.0
    glRotatef(moon_rotation, 0.0, 1.0, 0.0)
    
    # Aplicar textura y dibujar la luna
    glBindTexture(GL_TEXTURE_2D, texture)
    gluSphere(planet_sphere, radius, 16, 16)
    
    glPopMatrix()

# Función para cargar una textura desde un archivo
def load_texture(file_path):
    texture_surface = pygame.image.load(file_path)
    texture_data = pygame.image.tostring(texture_surface, "RGBA", True)
    width, height = texture_surface.get_size()
    
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
    
    return texture_id

# Cargar texturas para el skybox
skybox_textures = []
skybox_images = ["right.png", "left.png", "top.png", "bottom.png", "front.png", "back.png"]
skybox_dir = os.path.join("textures", "cubemap-space")

for img in skybox_images:
    texture_path = os.path.join(skybox_dir, img)
    skybox_textures.append(load_texture(texture_path))

# Cargar las texturas de los planetas
planets_dir = os.path.join("textures", "planets")

# Texturas de los planetas
sun_texture = load_texture(os.path.join(planets_dir, "Sun-map_baseColor.jpg"))
mercury_texture = load_texture(os.path.join(planets_dir, "Mercury-map_baseColor.jpeg"))
venus_texture = load_texture(os.path.join(planets_dir, "venus_baseColor.jpeg"))
earth_texture = load_texture(os.path.join(planets_dir, "Earth-map_baseColor.jpeg"))
mars_texture = load_texture(os.path.join(planets_dir, "Mars-map_baseColor.jpeg"))
jupiter_texture = load_texture(os.path.join(planets_dir, "Jupiter-map_baseColor.jpeg"))
saturn_texture = load_texture(os.path.join(planets_dir, "Saturn-map_baseColor.jpeg"))
saturn_rings_texture = load_texture(os.path.join(planets_dir, "rings_saturn_baseColor.png"))
uranus_texture = load_texture(os.path.join(planets_dir, "Uranus-map_baseColor.jpeg"))
uranus_rings_texture = load_texture(os.path.join(planets_dir, "rings_uranus-2_baseColor.png"))
neptune_texture = load_texture(os.path.join(planets_dir, "Neptune-map_baseColor.jpeg"))
moon_texture = load_texture(os.path.join(planets_dir, "Moon-map_baseColor.jpeg"))

# Función para crear una esfera
def create_sphere(radius, slices, stacks):
    sphere = gluNewQuadric()
    gluQuadricTexture(sphere, GL_TRUE)
    gluQuadricNormals(sphere, GLU_SMOOTH)
    return sphere

# Crear la esfera para los planetas
planet_sphere = gluNewQuadric()
gluQuadricTexture(planet_sphere, GL_TRUE)
gluQuadricNormals(planet_sphere, GLU_SMOOTH)

# Definición de los planetas (nombre, tamaño, distancia al sol, periodo orbital, periodo de rotación, inclinación)
planets_data = [
    # Nombre, Radio (Relativo), Distancia al Sol, Periodo orbital (año=1), Periodo rotación (día=1), Inclinación
    # A menor periodo orbital, más rápido orbita
    ["Mercury", 0.08, 2.5, 0.24, 58.6, 0.0],   # 0.24 años = 88 días
    ["Venus", 0.21, 3.5, 0.62, 243.0, 177.3],  # 0.62 años = 225 días
    ["Earth", 0.22, 5.0, 1.0, 1.0, 23.4],      # 1 año
    ["Mars", 0.12, 6.5, 1.88, 1.03, 25.2],     # 1.88 años
    ["Jupiter", 0.6, 9.0, 11.86, 0.41, 3.1],   # 11.86 años
    ["Saturn", 0.5, 12.0, 29.46, 0.45, 26.7],  # 29.46 años
    ["Uranus", 0.4, 15.5, 84.01, 0.72, 97.8],  # 84.01 años
    ["Neptune", 0.38, 19.0, 164.8, 0.67, 28.3] # 164.8 años
]

# Datos de la luna (nombre, radio, distancia al planeta, periodo orbital, periodo rotación)
moons_data = [
    # Nombre, Planeta padre, Radio, Distancia, Periodo orbital (días), Periodo rotación (días)
    ["Moon", "Earth", 0.06, 0.5, 27.3, 27.3]  # 27.3 días
]

# Clase para el controlador de cámara orbital
class OrbitCameraController:
    def __init__(self):
        self.radius = 5.0           # Distancia de la cámara al centro
        self.theta = 0.0            # Ángulo horizontal (rotación alrededor del eje Y)
        self.phi = 0.0              # Ángulo vertical (rotación alrededor del eje X)
        self.target = [0.0, 0.0, 0.0] # Punto al que mira la cámara
        self.up = [0.0, 1.0, 0.0]   # Vector "arriba" de la cámara
        self.sensitivity = 0.005    # Sensibilidad de rotación
        self.zoom_speed = 0.2       # Velocidad de zoom
        self.pan_speed = 0.01       # Velocidad de paneo
        self.drag_active = False    # Flag para seguimiento de arrastre
        self.right_drag_active = False # Flag para seguimiento de arrastre con botón derecho
        self.last_mouse_x = 0       # Última posición X del mouse
        self.last_mouse_y = 0       # Última posición Y del mouse
        
        # Límites para el ángulo phi para evitar dar la vuelta completa
        self.phi_min = -1.5  # Aproximadamente -85 grados
        self.phi_max = 1.5   # Aproximadamente 85 grados
        
        # Variables para seguimiento de planetas
        self.follow_planet = None   # Nombre del planeta a seguir (None = no seguir ninguno)
        self.follow_distance = 1.0  # Distancia a mantener del planeta durante el seguimiento
        self.follow_offset_y = 0.5  # Desplazamiento vertical para ver desde arriba
    
    def update(self, planet_positions=None):
        # Si estamos siguiendo un planeta, actualizar el objetivo
        if self.follow_planet and planet_positions and self.follow_planet in planet_positions:
            # Obtener la posición actual del planeta
            planet_pos = planet_positions[self.follow_planet]
            # Actualizar el objetivo de la cámara para que coincida con el planeta
            self.target = list(planet_pos)
        
        # Actualizar la cámara basada en los ángulos y la distancia
        x = self.radius * math.sin(self.theta) * math.cos(self.phi)
        z = self.radius * math.cos(self.theta) * math.cos(self.phi)
        y = self.radius * math.sin(self.phi)
        
        # Aplicar transformación de vista
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Configurar la posición de la cámara
        camera_pos = [
            x + self.target[0],
            y + self.target[1],
            z + self.target[2]
        ]
        
        # Configurar la vista usando gluLookAt
        gluLookAt(
            camera_pos[0], camera_pos[1], camera_pos[2],  # posición de la cámara
            self.target[0], self.target[1], self.target[2],  # punto al que mira
            self.up[0], self.up[1], self.up[2]  # vector "arriba"
        )
    
    def set_follow_planet(self, planet_name):
        # Establecer el planeta a seguir
        self.follow_planet = planet_name
        
        # Si no seguimos ningún planeta, volver al origen
        if planet_name is None:
            self.target = [0.0, 0.0, 0.0]
            self.radius = 5.0  # Distancia por defecto
        else:
            # Ajustar la distancia de la cámara según el planeta
            if planet_name == "Sun":
                self.radius = 3.0
            elif planet_name in ["Jupiter", "Saturn"]:
                self.radius = 2.0
            elif planet_name in ["Uranus", "Neptune"]:
                self.radius = 1.5
            elif planet_name in ["Earth", "Venus", "Mars"]:
                self.radius = 0.8
            elif planet_name == "Mercury":
                self.radius = 0.6
            else:
                self.radius = 1.0
    
    def handle_event(self, event, planet_positions=None):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Botón izquierdo
                # Si hacemos clic, verificar si hicimos clic en un planeta
                if planet_positions:
                    clicked_planet = self.check_planet_click(event.pos, planet_positions)
                    if clicked_planet:
                        print(f"Enfocando el planeta: {clicked_planet}")
                        self.set_follow_planet(clicked_planet)
                        return  # No activar drag si hicimos clic en un planeta
                
                # Activar arrastre solo si no estamos siguiendo un planeta
                if not self.follow_planet:
                    self.drag_active = True
                self.last_mouse_x, self.last_mouse_y = pygame.mouse.get_pos()
            
            elif event.button == 3:  # Botón derecho
                # El botón derecho para paneo
                self.right_drag_active = True
                self.last_mouse_x, self.last_mouse_y = pygame.mouse.get_pos()
            
            elif event.button == 4:  # Rueda arriba
                self.radius -= self.zoom_speed * self.radius
                if self.radius < 0.1:
                    self.radius = 0.1
            
            elif event.button == 5:  # Rueda abajo
                self.radius += self.zoom_speed * self.radius
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.drag_active = False
            elif event.button == 3:
                self.right_drag_active = False
                
        elif event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            delta_x = mouse_x - self.last_mouse_x
            delta_y = mouse_y - self.last_mouse_y
            
            if self.drag_active and not self.follow_planet:  # Rotación solo si no seguimos un planeta
                self.theta -= delta_x * self.sensitivity
                self.phi += delta_y * self.sensitivity
                
                # Limitar phi para evitar giros completos
                if self.phi > self.phi_max:
                    self.phi = self.phi_max
                if self.phi < self.phi_min:
                    self.phi = self.phi_min
            
            elif self.right_drag_active or (self.follow_planet and self.drag_active):  # Paneo (botón derecho) o rotación alrededor del planeta
                if self.follow_planet and self.drag_active:
                    # Si seguimos un planeta y arrastramos, rotar alrededor del planeta
                    self.theta -= delta_x * self.sensitivity
                    self.phi += delta_y * self.sensitivity
                    
                    # Limitar phi para evitar giros completos
                    if self.phi > self.phi_max:
                        self.phi = self.phi_max
                    if self.phi < self.phi_min:
                        self.phi = self.phi_min
                else:
                    # Paneo normal (botón derecho)
                    # Calcular vectores de dirección derecha y arriba en el espacio de la cámara
                    right_vector = [
                        math.cos(self.theta),
                        0,
                        -math.sin(self.theta)
                    ]
                    
                    # Mover el target según el movimiento del mouse
                    self.target[0] -= right_vector[0] * delta_x * self.pan_speed * self.radius
                    self.target[2] -= right_vector[2] * delta_x * self.pan_speed * self.radius
                    self.target[1] += delta_y * self.pan_speed * self.radius
                
            self.last_mouse_x = mouse_x
            self.last_mouse_y = mouse_y
    
    def check_planet_click(self, mouse_pos, planet_positions):
        # Convertir coordenadas del mouse a coordenadas OpenGL
        x, y = mouse_pos
        viewport = glGetIntegerv(GL_VIEWPORT)
        y = viewport[3] - y  # Invertir Y porque OpenGL tiene origen abajo-izquierda
        
        # Obtener las matrices
        modelview_matrix = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection_matrix = glGetDoublev(GL_PROJECTION_MATRIX)
        
        # Crear un rayo desde la cámara hacia el mouse
        # Obtener punto cercano (z=0) y lejano (z=1) del rayo
        try:
            near_x, near_y, near_z = gluUnProject(x, y, 0.0, modelview_matrix, projection_matrix, viewport)
            far_x, far_y, far_z = gluUnProject(x, y, 1.0, modelview_matrix, projection_matrix, viewport)
        except:
            return None
        
        # Vector dirección del rayo
        ray_dir = np.array([far_x - near_x, far_y - near_y, far_z - near_z])
        ray_dir = ray_dir / np.linalg.norm(ray_dir)  # Normalizar
        ray_origin = np.array([near_x, near_y, near_z])
        
        closest_planet = None
        min_distance = float('inf')
        
        # Verificar el Sol primero (posición fija en el origen)
        sun_pos = np.array([0.0, 0.0, 0.0])
        sun_radius = 1.0 * 1.5  # Radio del sol con tolerancia
        
        # Calcular intersección rayo-esfera para el Sol
        distance_to_sun = self.ray_sphere_intersection(ray_origin, ray_dir, sun_pos, sun_radius)
        if distance_to_sun is not None and distance_to_sun < min_distance:
            closest_planet = "Sun"
            min_distance = distance_to_sun
        
        # Verificar planetas
        for planet_name, position in planet_positions.items():
            if planet_name == "Sun":
                continue  # Ya verificamos el Sol
            
            planet_pos = np.array(position)
            
            # Encontrar el radio del planeta
            planet_radius = 0.1  # Valor por defecto
            for p in planets_data:
                if p[0] == planet_name:
                    planet_radius = p[1] * 2.5  # Aumentar tolerancia para clicks más fáciles
                    break
            
            # Calcular intersección rayo-esfera
            distance = self.ray_sphere_intersection(ray_origin, ray_dir, planet_pos, planet_radius)
            if distance is not None and distance < min_distance:
                closest_planet = planet_name
                min_distance = distance
        
        return closest_planet
    
    def ray_sphere_intersection(self, ray_origin, ray_dir, sphere_center, sphere_radius):
        """
        Calcula la intersección entre un rayo y una esfera.
        Retorna la distancia al punto de intersección más cercano, o None si no hay intersección.
        """
        # Vector del origen del rayo al centro de la esfera
        oc = ray_origin - sphere_center
        
        # Coeficientes de la ecuación cuadrática
        a = np.dot(ray_dir, ray_dir)
        b = 2.0 * np.dot(oc, ray_dir)
        c = np.dot(oc, oc) - sphere_radius * sphere_radius
        
        # Discriminante
        discriminant = b * b - 4 * a * c
        
        if discriminant < 0:
            return None  # No hay intersección
        
        # Calcular las dos soluciones
        sqrt_discriminant = math.sqrt(discriminant)
        t1 = (-b - sqrt_discriminant) / (2 * a)
        t2 = (-b + sqrt_discriminant) / (2 * a)
        
        # Retornar la intersección más cercana que sea positiva (delante de la cámara)
        if t1 > 0:
            return t1
        elif t2 > 0:
            return t2
        else:
            return None  # Intersección detrás de la cámara

# Crear el controlador de cámara
camera_controller = OrbitCameraController()

# Mostrar controles en consola
print("=== SIMULADOR DEL SISTEMA SOLAR ===")
print("Controles:")
print("- Click izquierdo en un planeta: Enfocar planeta")
print("- Arrastrar (sin planeta enfocado): Rotar cámara")
print("- Arrastrar (con planeta enfocado): Rotar alrededor del planeta")
print("- Click derecho + arrastrar: Paneo de cámara")
print("- Rueda del mouse: Zoom")
print("- Tecla C: Cancelar enfoque y volver a cámara libre")
print("- +/-: Aumentar/disminuir velocidad de simulación")
print("- ESC: Salir")
print("====================================")

# Configuración de la proyección
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
gluPerspective(45, (width / height), 0.1, 100.0)

# Bucle principal
running = True
clock = pygame.time.Clock()
last_time = pygame.time.get_ticks()
simulation_time = 0
planet_positions = {}  # Inicializar diccionario de posiciones

while running:
    # Calcular el tiempo transcurrido
    current_time = pygame.time.get_ticks()
    delta_time = (current_time - last_time) / 1000.0  # Convertir a segundos
    last_time = current_time
    
    # Actualizar el tiempo de simulación
    simulation_time += delta_time * time_scale
    
    # Limpiar la pantalla
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Actualizar la posición de la cámara con las posiciones anteriores
    camera_controller.update(planet_positions)
    
    # Guardar la matriz actual
    glPushMatrix()
    
    # Dibujar el skybox
    def draw_skybox():
        # Tamaño del skybox
        size = 50.0
        
        # Desactivar depth test para dibujar el skybox al fondo
        glDepthMask(GL_FALSE)
        
        # Dibuja cada cara del skybox
        # Cara derecha (X+)
        glBindTexture(GL_TEXTURE_2D, skybox_textures[0])
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(size, -size, -size)
        glTexCoord2f(1, 0); glVertex3f(size, -size, size)
        glTexCoord2f(1, 1); glVertex3f(size, size, size)
        glTexCoord2f(0, 1); glVertex3f(size, size, -size)
        glEnd()
        
        # Cara izquierda (X-)
        glBindTexture(GL_TEXTURE_2D, skybox_textures[1])
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-size, -size, size)
        glTexCoord2f(1, 0); glVertex3f(-size, -size, -size)
        glTexCoord2f(1, 1); glVertex3f(-size, size, -size)
        glTexCoord2f(0, 1); glVertex3f(-size, size, size)
        glEnd()
        
        # Cara superior (Y+)
        glBindTexture(GL_TEXTURE_2D, skybox_textures[2])
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-size, size, -size)
        glTexCoord2f(1, 0); glVertex3f(size, size, -size)
        glTexCoord2f(1, 1); glVertex3f(size, size, size)
        glTexCoord2f(0, 1); glVertex3f(-size, size, size)
        glEnd()
        
        # Cara inferior (Y-)
        glBindTexture(GL_TEXTURE_2D, skybox_textures[3])
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-size, -size, size)
        glTexCoord2f(1, 0); glVertex3f(size, -size, size)
        glTexCoord2f(1, 1); glVertex3f(size, -size, -size)
        glTexCoord2f(0, 1); glVertex3f(-size, -size, -size)
        glEnd()
        
        # Cara frontal (Z+)
        glBindTexture(GL_TEXTURE_2D, skybox_textures[4])
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-size, -size, size)
        glTexCoord2f(1, 0); glVertex3f(size, -size, size)
        glTexCoord2f(1, 1); glVertex3f(size, size, size)
        glTexCoord2f(0, 1); glVertex3f(-size, size, size)
        glEnd()
        
        # Cara trasera (Z-)
        glBindTexture(GL_TEXTURE_2D, skybox_textures[5])
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(size, -size, -size)
        glTexCoord2f(1, 0); glVertex3f(-size, -size, -size)
        glTexCoord2f(1, 1); glVertex3f(-size, size, -size)
        glTexCoord2f(0, 1); glVertex3f(size, size, -size)
        glEnd()
        
        # Reactivar depth test
        glDepthMask(GL_TRUE)
    
    # Dibujar el skybox centrado en la cámara
    draw_skybox()
    
    # Definir la función para dibujar el sol
    def draw_sun():
        # Guardar estado actual
        glPushMatrix()
        
        # Configurar el material del sol para que parezca brillante
        # Desactivar iluminación para el sol - para que sea emisivo
        glDisable(GL_LIGHTING)
        
        # Color amarillo brillante para el sol
        glColor4f(1.0, 1.0, 0.7, 1.0)
        
        # Activar el blending para efecto de brillo
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        
        # Rotar el sol (rotación solar = ~25 días terrestres)
        # Aplicamos el mismo factor de desaceleración que los planetas
        rotation_slowdown = 30.0
        days_passed = simulation_time * 365.0 / rotation_slowdown
        sun_rotation = (days_passed / 25.0) * 360.0 % 360
        glRotatef(sun_rotation, 0, 1, 0)
        
        # Aplicar la textura del sol
        glBindTexture(GL_TEXTURE_2D, sun_texture)
        
        # Dibujar el sol como una esfera
        sun_size = 1.0
        sun_quad = gluNewQuadric()
        gluQuadricTexture(sun_quad, GL_TRUE)
        gluSphere(sun_quad, sun_size, 32, 32)
        
        # Dibujar brillo (glow) alrededor del sol
        glBindTexture(GL_TEXTURE_2D, 0)  # Desactivar textura
        glColor4f(1.0, 0.9, 0.5, 0.3)    # Color amarillo transparente
        
        glow_quad = gluNewQuadric()
        gluSphere(glow_quad, sun_size * 1.2, 16, 16)  # Esfera más grande para el brillo
        
        # Restaurar estado
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)
        glColor4f(1.0, 1.0, 1.0, 1.0)  # Restaurar color por defecto
        
        # Configurar luz posicional en el sol
        set_sun_light()
        
        glPopMatrix()
    
    # Dibujar el sol en el centro de la escena
    draw_sun()
    
    # Dibujar los planetas
    planet_positions = {}
    
    # Agregar la posición del Sol (siempre en el origen)
    planet_positions["Sun"] = (0.0, 0.0, 0.0)
    
    # Mercurio
    planet_positions["Mercury"] = draw_planet(
        mercury_texture, 
        planets_data[0][1],  # radio
        planets_data[0][2],  # distancia
        planets_data[0][3],  # periodo orbital
        planets_data[0][4],  # periodo rotación
        planets_data[0][5],  # inclinación
        simulation_time
    )
    
    # Venus
    planet_positions["Venus"] = draw_planet(
        venus_texture, 
        planets_data[1][1], 
        planets_data[1][2], 
        planets_data[1][3], 
        planets_data[1][4], 
        planets_data[1][5],
        simulation_time
    )
    
    # Tierra
    planet_positions["Earth"] = draw_planet(
        earth_texture, 
        planets_data[2][1], 
        planets_data[2][2], 
        planets_data[2][3], 
        planets_data[2][4], 
        planets_data[2][5],
        simulation_time
    )
    
    # Marte
    planet_positions["Mars"] = draw_planet(
        mars_texture, 
        planets_data[3][1], 
        planets_data[3][2], 
        planets_data[3][3], 
        planets_data[3][4], 
        planets_data[3][5],
        simulation_time
    )
    
    # Júpiter
    planet_positions["Jupiter"] = draw_planet(
        jupiter_texture, 
        planets_data[4][1], 
        planets_data[4][2], 
        planets_data[4][3], 
        planets_data[4][4], 
        planets_data[4][5],
        simulation_time
    )
    
    # Saturno y sus anillos
    saturn_pos = draw_planet(
        saturn_texture, 
        planets_data[5][1], 
        planets_data[5][2], 
        planets_data[5][3], 
        planets_data[5][4], 
        planets_data[5][5],
        simulation_time
    )
    planet_positions["Saturn"] = saturn_pos
    
    # Dibujar anillos de Saturno
    glPushMatrix()
    glTranslatef(saturn_pos[0], saturn_pos[1], saturn_pos[2])
    glRotatef(planets_data[5][5], 0, 0, 1)  # Inclinación de Saturno
    draw_rings(saturn_rings_texture, planets_data[5][1] * 1.2, planets_data[5][1] * 2.0, 100)
    glPopMatrix()
    
    # Urano y sus anillos
    uranus_pos = draw_planet(
        uranus_texture, 
        planets_data[6][1], 
        planets_data[6][2], 
        planets_data[6][3], 
        planets_data[6][4], 
        planets_data[6][5],
        simulation_time
    )
    planet_positions["Uranus"] = uranus_pos
    
    # Dibujar anillos de Urano
    glPushMatrix()
    glTranslatef(uranus_pos[0], uranus_pos[1], uranus_pos[2])
    glRotatef(planets_data[6][5], 0, 0, 1)  # Inclinación de Urano
    draw_rings(uranus_rings_texture, planets_data[6][1] * 1.1, planets_data[6][1] * 1.5, 100)
    glPopMatrix()
    
    # Neptuno
    planet_positions["Neptune"] = draw_planet(
        neptune_texture, 
        planets_data[7][1], 
        planets_data[7][2], 
        planets_data[7][3], 
        planets_data[7][4], 
        planets_data[7][5],
        simulation_time
    )
    
    # Dibujar la Luna de la Tierra
    draw_moon(
        moon_texture,
        planet_positions["Earth"],  # Posición de la Tierra (planeta padre)
        moons_data[0][2],  # Radio
        moons_data[0][3],  # Distancia
        moons_data[0][4],  # Periodo orbital
        moons_data[0][5],  # Periodo rotación
        simulation_time
    )
    
    # Restaurar la matriz
    glPopMatrix()
    
    # Manejo de eventos (después de calcular posiciones de planetas)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                time_scale *= 1.2  # Aumentar velocidad de simulación
            elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                time_scale /= 1.2  # Reducir velocidad de simulación
            elif event.key == pygame.K_c:  # Tecla C para cancelar enfoque
                if camera_controller.follow_planet:
                    print(f"Cancelando enfoque de: {camera_controller.follow_planet}")
                    camera_controller.set_follow_planet(None)
                    print("Modo cámara libre activado")
        
        # Pasar eventos al controlador de cámara con las posiciones de los planetas
        camera_controller.handle_event(event, planet_positions)
    
    # Actualizar la pantalla
    pygame.display.flip()
    clock.tick(60)  # 60 FPS

# Finalizar Pygame
pygame.quit()