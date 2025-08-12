import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import os
import math

# Inicializar Pygame
pygame.init()
pygame.font.init()
pygame.mouse.set_visible(True)

# Fuente para el texto
font = pygame.font.SysFont('Arial', 18)
big_font = pygame.font.SysFont('Arial', 24, bold=True)

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
time_scale = 0.5  # Velocidad de la simulación: 0.5 = medio "año" por segundo

# Variable para el planeta seleccionado
selected_planet = None
focused_planet = None

# Información detallada de los planetas
planet_info = {
    "Mercury": {
        "nombre": "Mercurio",
        "diametro": "4,879.4 km",
        "distancia_sol": "57.9 millones km",
        "periodo_orbital": "88 días",
        "periodo_rotacion": "59 días",
        "temperatura": "-173°C a 427°C",
        "descripcion": "El planeta más pequeño y más cercano al Sol, con una superficie similar a la Luna, llena de cráteres."
    },
    "Venus": {
        "nombre": "Venus",
        "diametro": "12,104 km",
        "distancia_sol": "108.2 millones km",
        "periodo_orbital": "225 días",
        "periodo_rotacion": "243 días (retrógrada)",
        "temperatura": "462°C",
        "descripcion": "Conocido como el gemelo de la Tierra por su tamaño similar, pero con una atmósfera densa de CO2 y efecto invernadero extremo."
    },
    "Earth": {
        "nombre": "Tierra",
        "diametro": "12,742 km",
        "distancia_sol": "149.6 millones km",
        "periodo_orbital": "365.25 días",
        "periodo_rotacion": "24 horas",
        "temperatura": "-88°C a 58°C",
        "descripcion": "Nuestro planeta hogar, el único conocido con agua líquida en su superficie y vida."
    },
    "Mars": {
        "nombre": "Marte",
        "diametro": "6,779 km",
        "distancia_sol": "227.9 millones km",
        "periodo_orbital": "687 días",
        "periodo_rotacion": "24.6 horas",
        "temperatura": "-153°C a 20°C",
        "descripcion": "El planeta rojo, con la montaña más alta del sistema solar (Olympus Mons) y cañones profundos."
    },
    "Jupiter": {
        "nombre": "Júpiter",
        "diametro": "139,820 km",
        "distancia_sol": "778.5 millones km",
        "periodo_orbital": "11.86 años",
        "periodo_rotacion": "9.9 horas",
        "temperatura": "-108°C",
        "descripcion": "El planeta más grande del sistema solar, un gigante gaseoso con la Gran Mancha Roja, una tormenta que dura siglos."
    },
    "Saturn": {
        "nombre": "Saturno",
        "diametro": "116,460 km",
        "distancia_sol": "1,434 millones km",
        "periodo_orbital": "29.46 años",
        "periodo_rotacion": "10.7 horas",
        "temperatura": "-139°C",
        "descripcion": "Famoso por sus espectaculares anillos compuestos principalmente de partículas de hielo y roca."
    },
    "Uranus": {
        "nombre": "Urano",
        "diametro": "50,724 km",
        "distancia_sol": "2,871 millones km",
        "periodo_orbital": "84.01 años",
        "periodo_rotacion": "17.2 horas (retrógrada)",
        "temperatura": "-197°C",
        "descripcion": "Gigante de hielo con un eje de rotación inclinado casi 98 grados, prácticamente 'rodando' en su órbita."
    },
    "Neptune": {
        "nombre": "Neptuno",
        "diametro": "49,244 km",
        "distancia_sol": "4,495 millones km",
        "periodo_orbital": "164.8 años",
        "periodo_rotacion": "16.1 horas",
        "temperatura": "-201°C",
        "descripcion": "El planeta más lejano, con los vientos más rápidos del sistema solar (hasta 2,100 km/h)."
    },
    "Sun": {
        "nombre": "Sol",
        "diametro": "1,392,684 km",
        "distancia_sol": "0 km",
        "periodo_orbital": "225-250 millones años (alrededor del centro galáctico)",
        "periodo_rotacion": "25-35 días (varía según latitud)",
        "temperatura": "5,500°C (superficie), 15 millones °C (núcleo)",
        "descripcion": "La estrella central del sistema solar, compuesta principalmente de hidrógeno y helio, genera energía mediante fusión nuclear."
    }
}

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

# Función para dibujar un planeta
def draw_planet(texture, radius, distance, orbit_period, rotation_period, tilt, time, name):
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
    
    # Guardar nombre y posición del planeta para detección de clics
    planet_screen_pos = get_screen_pos(x, 0.0, z)
    
    # Dibujar el planeta
    gluSphere(planet_sphere, radius, 32, 32)
    
    # Devolver la posición para posibles lunas
    pos = (x, 0.0, z)
    
    glPopMatrix()
    
    # Si este es el planeta enfocado, actualizar el objetivo de la cámara
    global focused_planet
    if focused_planet == name:
        camera_controller.target = [x, 0.0, z]
    
    # Devolver posición en coordenadas de mundo y pantalla
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

# Función para convertir coordenadas 3D a coordenadas de pantalla
def get_screen_pos(x, y, z):
    # Obtener matrices actuales
    modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
    projection = glGetDoublev(GL_PROJECTION_MATRIX)
    viewport = glGetIntegerv(GL_VIEWPORT)
    
    # Convertir coordenadas 3D a coordenadas de pantalla
    screen_x, screen_y, screen_z = gluProject(x, y, z, modelview, projection, viewport)
    
    return (screen_x, height - screen_y, screen_z)  # Invertir Y para coincidencia con Pygame

# Función para detectar clic en planeta
def detect_planet_click(mouse_pos, planet_positions, planet_radii):
    closest_planet = None
    min_dist = float('inf')
    
    for name, pos in planet_positions.items():
        # Convertir posición 3D a coordenadas de pantalla
        screen_pos = get_screen_pos(pos[0], pos[1], pos[2])
        
        # Calcular distancia en 2D (pantalla)
        dist = math.sqrt((mouse_pos[0] - screen_pos[0])**2 + (mouse_pos[1] - screen_pos[1])**2)
        
        # El tamaño del planeta en pantalla depende de su radio y distancia a la cámara
        # Aquí usamos una aproximación simple multiplicando por un factor
        screen_radius = planet_radii[name] * 100  # Factor arbitrario para ajustar al tamaño visual
        
        # Si el clic está dentro del radio del planeta y es el más cercano hasta ahora
        if dist < screen_radius and dist < min_dist:
            min_dist = dist
            closest_planet = name
    
    return closest_planet

# Función para dibujar el panel de información
def draw_info_panel(planet_name):
    if planet_name is None or planet_name not in planet_info:
        return
    
    info = planet_info[planet_name]
    
    # Configurar superficie para dibujar texto
    panel_width, panel_height = 300, 210
    panel_x, panel_y = 20, 20
    
    # Dibujar superficie semitransparente
    surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    surface.fill((0, 0, 30, 200))  # Azul muy oscuro semitransparente
    
    # Dibujar título
    title_surface = big_font.render(info["nombre"], True, (255, 255, 255))
    surface.blit(title_surface, (10, 10))
    
    # Dibujar información
    y_offset = 45
    line_height = 22
    
    # Datos principales
    info_items = [
        f"Diámetro: {info['diametro']}",
        f"Distancia al Sol: {info['distancia_sol']}",
        f"Año: {info['periodo_orbital']}",
        f"Día: {info['periodo_rotacion']}",
        f"Temperatura: {info['temperatura']}"
    ]
    
    for item in info_items:
        text_surface = font.render(item, True, (200, 200, 255))
        surface.blit(text_surface, (15, y_offset))
        y_offset += line_height
    
    # Descripción con posible wrap
    desc_words = info["descripcion"].split()
    line = ""
    for word in desc_words:
        test_line = line + word + " "
        test_surface = font.render(test_line, True, (200, 200, 255))
        if test_surface.get_width() > panel_width - 30:
            text_surface = font.render(line, True, (200, 200, 255))
            surface.blit(text_surface, (15, y_offset))
            y_offset += line_height
            line = word + " "
        else:
            line = test_line
    
    # Última línea de descripción
    if line:
        text_surface = font.render(line, True, (200, 200, 255))
        surface.blit(text_surface, (15, y_offset))
    
    # Convertir a formato OpenGL y dibujar en pantalla
    surface_data = pygame.image.tostring(surface, "RGBA", True)
    
    # Guardar estado de OpenGL
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)
    
    # Configurar proyección ortográfica para dibujar en 2D
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, width, 0, height, -1, 1)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Crear y configurar textura
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, panel_width, panel_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, surface_data)
    
    # Dibujar cuadro texturizado
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(panel_x, panel_y)
    glTexCoord2f(1, 0); glVertex2f(panel_x + panel_width, panel_y)
    glTexCoord2f(1, 1); glVertex2f(panel_x + panel_width, panel_y + panel_height)
    glTexCoord2f(0, 1); glVertex2f(panel_x, panel_y + panel_height)
    glEnd()
    
    # Restaurar estado OpenGL
    glDisable(GL_BLEND)
    glDeleteTextures(1, [texture])
    
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_TEXTURE_2D)

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
    
    def update(self):
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
    
    def handle_event(self, event):
        global selected_planet, focused_planet
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Botón izquierdo
                # Primero verificamos si se hizo clic en un planeta
                # La detección del planeta seleccionado se maneja fuera de esta clase
                # Si no hay planeta seleccionado, activamos el arrastre normal
                if not selected_planet:
                    self.drag_active = True
                    self.last_mouse_x, self.last_mouse_y = pygame.mouse.get_pos()
                # Si hay planeta seleccionado, actualiza el planeta enfocado
                else:
                    focused_planet = selected_planet
                    selected_planet = None  # Reseteamos para el siguiente clic
                    
            elif event.button == 3:  # Botón derecho
                self.right_drag_active = True
                self.last_mouse_x, self.last_mouse_y = pygame.mouse.get_pos()
                # Al hacer clic derecho, cancelamos cualquier seguimiento de planeta
                focused_planet = None
                
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
            
            if self.drag_active:  # Rotación (botón izquierdo)
                self.theta -= delta_x * self.sensitivity
                self.phi += delta_y * self.sensitivity
                
                # Limitar phi para evitar giros completos
                if self.phi > self.phi_max:
                    self.phi = self.phi_max
                if self.phi < self.phi_min:
                    self.phi = self.phi_min
            
            elif self.right_drag_active:  # Paneo (botón derecho)
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

# Crear el controlador de cámara
camera_controller = OrbitCameraController()

# Configuración de la proyección
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
gluPerspective(45, (width / height), 0.1, 100.0)

# Bucle principal
running = True
clock = pygame.time.Clock()
last_time = pygame.time.get_ticks()
simulation_time = 0

while running:
    # Calcular el tiempo transcurrido
    current_time = pygame.time.get_ticks()
    delta_time = (current_time - last_time) / 1000.0  # Convertir a segundos
    last_time = current_time
    
    # Actualizar el tiempo de simulación
    simulation_time += delta_time * time_scale
    
    # Manejo de eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                time_scale *= 1.2  # Aumentar velocidad de simulación (factor más pequeño)
            elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                time_scale /= 1.2  # Reducir velocidad de simulación (factor más pequeño)
        
        # Pasar eventos al controlador de cámara
        camera_controller.handle_event(event)
    
    # Limpiar la pantalla
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Actualizar la posición de la cámara
    camera_controller.update()
    
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
        
        # Si el sol es el planeta enfocado, actualizar target
        if focused_planet == "Sun":
            camera_controller.target = [0.0, 0.0, 0.0]
    
    # Dibujar el sol en el centro de la escena
    draw_sun()
    
    # Almacenar las posiciones y radios de los planetas para detección de clics
    planet_positions = {}
    planet_radii = {"Sun": 1.0}  # Añadir el sol
    
    # Dibujar los planetas
    # Mercurio
    planet_positions["Mercury"] = draw_planet(
        mercury_texture, 
        planets_data[0][1],  # radio
        planets_data[0][2],  # distancia
        planets_data[0][3],  # periodo orbital
        planets_data[0][4],  # periodo rotación
        planets_data[0][5],  # inclinación
        simulation_time,
        "Mercury"
    )
    planet_radii["Mercury"] = planets_data[0][1]
    
    # Venus
    planet_positions["Venus"] = draw_planet(
        venus_texture, 
        planets_data[1][1], 
        planets_data[1][2], 
        planets_data[1][3], 
        planets_data[1][4], 
        planets_data[1][5],
        simulation_time,
        "Venus"
    )
    planet_radii["Venus"] = planets_data[1][1]
    
    # Tierra
    planet_positions["Earth"] = draw_planet(
        earth_texture, 
        planets_data[2][1], 
        planets_data[2][2], 
        planets_data[2][3], 
        planets_data[2][4], 
        planets_data[2][5],
        simulation_time,
        "Earth"
    )
    planet_radii["Earth"] = planets_data[2][1]
    
    # Marte
    planet_positions["Mars"] = draw_planet(
        mars_texture, 
        planets_data[3][1], 
        planets_data[3][2], 
        planets_data[3][3], 
        planets_data[3][4], 
        planets_data[3][5],
        simulation_time,
        "Mars"
    )
    planet_radii["Mars"] = planets_data[3][1]
    
    # Júpiter
    planet_positions["Jupiter"] = draw_planet(
        jupiter_texture, 
        planets_data[4][1], 
        planets_data[4][2], 
        planets_data[4][3], 
        planets_data[4][4], 
        planets_data[4][5],
        simulation_time,
        "Jupiter"
    )
    planet_radii["Jupiter"] = planets_data[4][1]
    
    # Saturno y sus anillos
    saturn_pos = draw_planet(
        saturn_texture, 
        planets_data[5][1], 
        planets_data[5][2], 
        planets_data[5][3], 
        planets_data[5][4], 
        planets_data[5][5],
        simulation_time,
        "Saturn"
    )
    planet_positions["Saturn"] = saturn_pos
    planet_radii["Saturn"] = planets_data[5][1]
    
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
        simulation_time,
        "Uranus"
    )
    planet_positions["Uranus"] = uranus_pos
    planet_radii["Uranus"] = planets_data[6][1]
    
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
        simulation_time,
        "Neptune"
    )
    planet_radii["Neptune"] = planets_data[7][1]
    
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
    
    # Detectar clic en planeta (cuando se hace clic)
    mouse_buttons = pygame.mouse.get_pressed()
    if mouse_buttons[0]:  # Botón izquierdo
        mouse_pos = pygame.mouse.get_pos()
        selected_planet = detect_planet_click(mouse_pos, planet_positions, planet_radii)
    
    # Dibujar panel de información si hay un planeta seleccionado
    if focused_planet:
        draw_info_panel(focused_planet)
    
    # Actualizar la pantalla
    pygame.display.flip()
    clock.tick(60)  # 60 FPS

# Finalizar Pygame
pygame.quit()
