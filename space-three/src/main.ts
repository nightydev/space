import './style.css';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

// Limpiamos el contenido predeterminado
document.querySelector<HTMLDivElement>('#app')!.innerHTML = '';

// Configuración de la escena
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);
camera.position.z = 5;

// Configuración del renderer
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
// Cambiar a ReinhardToneMapping para un look más suave en las áreas luminosas
renderer.toneMapping = THREE.ReinhardToneMapping;
renderer.toneMappingExposure = 0.8; // Menor exposición para reducir dureza
document.querySelector('#app')!.appendChild(renderer.domElement);

// Configuración de los controles de órbita
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true; // Para animación suave
controls.dampingFactor = 0.05;
controls.enableZoom = true;
controls.minDistance = 2; // Distancia mínima para el zoom
controls.maxDistance = 40; // Distancia máxima para ver todo el sistema
controls.update();

// Crear el skybox con cubemap
const loader = new THREE.CubeTextureLoader();
loader.setPath('/textures/cubemap-space/');

const textureCube = loader.load([
  'right.png', // positiveX
  'left.png',  // negativeX
  'top.png',   // positiveY
  'bottom.png', // negativeY
  'front.png', // positiveZ
  'back.png'   // negativeZ
]);
scene.background = textureCube;

// Crear el Sol
const sunRadius = 1;
const sunGeometry = new THREE.SphereGeometry(sunRadius, 32, 32);

// Cargar la textura del Sol
const textureLoader = new THREE.TextureLoader();
const sunTexture = textureLoader.load('/textures/planets/Sun-map_baseColor.jpg');

// Material para el Sol con emisión de luz
const sunMaterial = new THREE.MeshStandardMaterial({
  map: sunTexture,
  emissive: 0xff7700, // Color naranja-amarillo más cálido para la emisión
  emissiveMap: sunTexture, // Usar la misma textura para el mapa de emisión
  emissiveIntensity: 5, // Reducir intensidad de emisión para un efecto más suave
});

const sun = new THREE.Mesh(sunGeometry, sunMaterial);
scene.add(sun);

// Crear un sistema de múltiples capas de halo para efecto más difuminado
// Primera capa - cercana y más intensa
const sunGlowGeometry1 = new THREE.SphereGeometry(sunRadius * 1.1, 32, 32);
const sunGlowMaterial1 = new THREE.MeshBasicMaterial({
  color: 0xff7700,
  transparent: true,
  opacity: 0.2,
  side: THREE.BackSide
});
const sunGlow1 = new THREE.Mesh(sunGlowGeometry1, sunGlowMaterial1);
scene.add(sunGlow1);

// Añadir luces para simular el brillo del Sol de forma más suave
// Luz puntual en el centro del Sol con menos intensidad para reducir el efecto duro
const sunLight = new THREE.PointLight(0xffffff, 10, 100);
sunLight.position.set(0, 0, 0);
// Añadir penumbra para suavizar los bordes de las sombras
sunLight.decay = 2; // Atenuación física más realista
scene.add(sunLight);

// Segunda luz puntual con más radio para una iluminación más difusa
const sunLightOuter = new THREE.PointLight(0xffeecc, 0.6, 150);
sunLightOuter.position.set(0, 0, 0);
scene.add(sunLightOuter);

// Luz ambiental más intensa para iluminar la escena de forma más uniforme
const ambientLight = new THREE.AmbientLight(0x444444);
scene.add(ambientLight);

// Creación de los planetas
// Función para crear un planeta
function createPlanet(
  radius: number,
  texturePath: string,
  distanceFromSun: number,
  rotationSpeed: number,
  orbitSpeed: number
) {
  // Geometría y material del planeta
  const planetGeometry = new THREE.SphereGeometry(radius, 32, 16);
  const planetTexture = textureLoader.load(texturePath);
  const planetMaterial = new THREE.MeshStandardMaterial({
    map: planetTexture,
    roughness: 0.8,
    metalness: 0.1,
  });

  // Crear el mesh del planeta
  const planet = new THREE.Mesh(planetGeometry, planetMaterial);

  // Crear un objeto contenedor para la órbita
  const orbitContainer = new THREE.Object3D();
  scene.add(orbitContainer);
  orbitContainer.add(planet);

  // Posicionar el planeta a la distancia del sol
  planet.position.x = distanceFromSun;

  // Añadir información adicional al objeto para la animación
  planet.userData = {
    rotationSpeed: rotationSpeed,
    orbitSpeed: orbitSpeed,
    distanceFromSun: distanceFromSun
  };

  // Crear la línea de la órbita
  const orbitGeometry = new THREE.BufferGeometry();
  const orbitMaterial = new THREE.LineBasicMaterial({ color: 0x444444, transparent: true, opacity: 0.3 });

  // Generar puntos para la órbita circular
  const orbitPoints = [];
  const orbitSegments = 128;
  for (let i = 0; i <= orbitSegments; i++) {
    const angle = (i / orbitSegments) * Math.PI * 2;
    orbitPoints.push(
      Math.cos(angle) * distanceFromSun,
      0,
      Math.sin(angle) * distanceFromSun
    );
  }

  orbitGeometry.setAttribute('position', new THREE.Float32BufferAttribute(orbitPoints, 3));
  const orbit = new THREE.Line(orbitGeometry, orbitMaterial);
  scene.add(orbit);

  return { planet, orbitContainer };
}

// Crear los planetas con sus datos específicos (radio, textura, distancia, velocidad de rotación, velocidad orbital)
// Los valores son aproximados para una buena visualización en escala relativa

// Mercurio
const mercury = createPlanet(
  0.08,
  '/textures/planets/Mercury-map_baseColor.jpeg',
  1.8,
  0.004,
  0.008
);

// Venus
const venus = createPlanet(
  0.2,
  '/textures/planets/venus_baseColor.jpeg',
  2.5,
  0.002,
  0.006
);

// Tierra
const earth = createPlanet(
  0.22,
  '/textures/planets/Earth-map_baseColor.jpeg',
  3.5,
  0.003,
  0.004
);

// Marte
const mars = createPlanet(
  0.15,
  '/textures/planets/Mars-map_baseColor.jpeg',
  4.5,
  0.0025,
  0.003
);

// Júpiter
const jupiter = createPlanet(
  0.5,
  '/textures/planets/Jupiter-map_baseColor.jpeg',
  6.0,
  0.004,
  0.002
);

// Saturno (con anillos)
const saturn = createPlanet(
  0.4,
  '/textures/planets/Saturn-map_baseColor.jpeg',
  8.0,
  0.0038,
  0.0015
);

// Anillos de Saturno
const saturnRingGeometry = new THREE.RingGeometry(0.55, 0.75, 64);
const saturnRingTexture = textureLoader.load('/textures/planets/rings_saturn_baseColor.png');
const saturnRingMaterial = new THREE.MeshStandardMaterial({
  map: saturnRingTexture,
  side: THREE.DoubleSide,
  transparent: true,
  opacity: 0.9,
});

const saturnRing = new THREE.Mesh(saturnRingGeometry, saturnRingMaterial);
saturnRing.rotation.x = Math.PI / 2 + 0.3; // Inclinación de los anillos
saturn.planet.add(saturnRing);

// Urano
const uranus = createPlanet(
  0.3,
  '/textures/planets/Uranus-map_baseColor.jpeg',
  9.5,
  0.003,
  0.001
);

// Anillos de Urano
const uranusRingGeometry = new THREE.RingGeometry(0.4, 0.45, 64);
const uranusRingTexture = textureLoader.load('/textures/planets/rings_uranus-2_baseColor.png');
const uranusRingMaterial = new THREE.MeshStandardMaterial({
  map: uranusRingTexture,
  side: THREE.DoubleSide,
  transparent: true,
  opacity: 0.7,
});

const uranusRing = new THREE.Mesh(uranusRingGeometry, uranusRingMaterial);
uranusRing.rotation.x = Math.PI / 2 + 0.8; // Inclinación pronunciada de los anillos
uranus.planet.add(uranusRing);

// Neptuno
const neptune = createPlanet(
  0.28,
  '/textures/planets/Neptune-map_baseColor.jpeg',
  11.0,
  0.0032,
  0.0008
);

// La luna
const moon = createPlanet(
  0.06,
  '/textures/planets/Moon-map_baseColor.jpeg',
  0.5, // Distancia a la Tierra
  0.002,
  0.02
);

// Quitar la luna de la escena y añadirla a la Tierra
scene.remove(moon.orbitContainer);
earth.planet.add(moon.planet);
moon.planet.position.set(0.5, 0, 0); // Posición respecto a la Tierra

// Ajustar la cámara para una mejor vista del sistema
camera.position.set(0, 5, 15);
controls.update();

// Información de los planetas
const planetInfo = {
  sun: {
    name: "Sol",
    diameter: "1.392.700 km",
    description: "El Sol es la estrella central del Sistema Solar. Es una esfera casi perfecta de plasma caliente, con movimientos de convección interna que generan un campo magnético a través de un proceso de dinamo. Es, con diferencia, la fuente de energía más importante para la vida en la Tierra.",
    distanceFromSun: "0 km (es el centro)",
    orbitalPeriod: "N/A",
    rotationPeriod: "25-35 días (varía según la latitud)",
    temperature: "5.500°C (superficie), 15.000.000°C (núcleo)"
  },
  mercury: {
    name: "Mercurio",
    diameter: "4.879 km",
    description: "Mercurio es el planeta más pequeño y más interno del Sistema Solar. Su órbita alrededor del Sol tarda 87,97 días terrestres, el más breve de todos los planetas. Su superficie está llena de cráteres de impacto, similar a la Luna terrestre.",
    distanceFromSun: "57.9 millones km",
    orbitalPeriod: "88 días",
    rotationPeriod: "59 días",
    temperature: "-173°C a 427°C"
  },
  venus: {
    name: "Venus",
    diameter: "12.104 km",
    description: "Venus es el segundo planeta del Sistema Solar. Es un planeta terrestre similar a la Tierra en tamaño y masa, pero sus condiciones superficiales son extremas debido a una atmósfera densa de dióxido de carbono que genera un intenso efecto invernadero.",
    distanceFromSun: "108.2 millones km",
    orbitalPeriod: "225 días",
    rotationPeriod: "243 días (retrógrado)",
    temperature: "462°C (promedio)"
  },
  earth: {
    name: "Tierra",
    diameter: "12.742 km",
    description: "La Tierra es el tercer planeta del Sistema Solar y el único conocido que alberga vida. Tiene una atmósfera rica en nitrógeno y oxígeno, y es el único planeta con agua líquida en su superficie, cubriendo el 71% de la misma.",
    distanceFromSun: "149.6 millones km",
    orbitalPeriod: "365.25 días",
    rotationPeriod: "24 horas",
    temperature: "-88°C a 58°C"
  },
  mars: {
    name: "Marte",
    diameter: "6.779 km",
    description: "Marte es el cuarto planeta del Sistema Solar. Conocido como el 'planeta rojo' debido a la abundancia de óxido de hierro en su superficie, tiene dos pequeñas lunas, una atmósfera tenue y es objetivo de numerosas misiones de exploración espacial.",
    distanceFromSun: "227.9 millones km",
    orbitalPeriod: "687 días",
    rotationPeriod: "24 horas y 37 minutos",
    temperature: "-153°C a 20°C"
  },
  jupiter: {
    name: "Júpiter",
    diameter: "139.820 km",
    description: "Júpiter es el planeta más grande del Sistema Solar. Es un gigante gaseoso compuesto principalmente de hidrógeno y helio, con una característica Gran Mancha Roja, una tormenta anticiclónica masiva que ha existido durante siglos.",
    distanceFromSun: "778.5 millones km",
    orbitalPeriod: "11.86 años",
    rotationPeriod: "9 horas y 56 minutos",
    temperature: "-145°C (nubes superiores)"
  },
  saturn: {
    name: "Saturno",
    diameter: "116.460 km",
    description: "Saturno es el sexto planeta del Sistema Solar y es famoso por su impresionante sistema de anillos, compuestos principalmente de partículas de hielo y roca. Es un gigante gaseoso similar a Júpiter pero menos masivo.",
    distanceFromSun: "1.434 millones km",
    orbitalPeriod: "29.46 años",
    rotationPeriod: "10 horas y 33 minutos",
    temperature: "-178°C (nubes superiores)"
  },
  uranus: {
    name: "Urano",
    diameter: "50.724 km",
    description: "Urano es el séptimo planeta del Sistema Solar. Es un gigante de hielo con una composición similar a Neptuno. Tiene la característica única de rotar sobre un eje casi paralelo a su órbita, como si rodara por su trayectoria.",
    distanceFromSun: "2.871 millones km",
    orbitalPeriod: "84.01 años",
    rotationPeriod: "17 horas y 14 minutos (retrógrado)",
    temperature: "-224°C"
  },
  neptune: {
    name: "Neptuno",
    diameter: "49.244 km",
    description: "Neptuno es el octavo y más distante planeta del Sistema Solar. Es un gigante de hielo similar a Urano, con una atmósfera dinámica caracterizada por sus tormentas y vientos supersónicos, siendo la Gran Mancha Oscura su característica más notable.",
    distanceFromSun: "4.495 millones km",
    orbitalPeriod: "164.8 años",
    rotationPeriod: "16 horas y 6 minutos",
    temperature: "-218°C"
  },
  moon: {
    name: "Luna",
    diameter: "3.474 km",
    description: "La Luna es el único satélite natural de la Tierra. Es el quinto satélite más grande del Sistema Solar y el más grande en proporción a su planeta. Su influencia gravitatoria produce las mareas oceánicas y una ligera ralentización de la rotación de la Tierra.",
    distanceFromSun: "149.6 millones km (igual que la Tierra)",
    distanceFromEarth: "384.400 km",
    orbitalPeriod: "27.3 días (alrededor de la Tierra)",
    rotationPeriod: "27.3 días (rotación síncrona)",
    temperature: "-173°C a 127°C"
  }
};

// Crear un panel de información HTML
const infoPanel = document.createElement('div');
infoPanel.style.position = 'absolute';
infoPanel.style.bottom = '20px';
infoPanel.style.left = '20px';
infoPanel.style.width = '300px';
infoPanel.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
infoPanel.style.color = 'white';
infoPanel.style.padding = '15px';
infoPanel.style.borderRadius = '10px';
infoPanel.style.fontFamily = 'Arial, sans-serif';
infoPanel.style.fontSize = '14px';
infoPanel.style.display = 'none';
infoPanel.style.zIndex = '1000';
infoPanel.style.maxHeight = '400px';
infoPanel.style.overflowY = 'auto';
infoPanel.style.backdropFilter = 'blur(10px)';
infoPanel.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.5)';
document.body.appendChild(infoPanel);

// Configuración para seleccionar planetas
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
let selectedObject: THREE.Object3D | null = null;
let currentFocusTarget: THREE.Object3D | null = null;
let originalCameraPosition = new THREE.Vector3(0, 5, 15);
let cameraAnimationInProgress = false;

// Crear un mapa para asociar objetos 3D con sus datos
const objectInfoMap = new Map();

// Asociar objetos con sus datos
objectInfoMap.set(sun, planetInfo.sun);
objectInfoMap.set(mercury.planet, planetInfo.mercury);
objectInfoMap.set(venus.planet, planetInfo.venus);
objectInfoMap.set(earth.planet, planetInfo.earth);
objectInfoMap.set(mars.planet, planetInfo.mars);
objectInfoMap.set(jupiter.planet, planetInfo.jupiter);
objectInfoMap.set(saturn.planet, planetInfo.saturn);
objectInfoMap.set(uranus.planet, planetInfo.uranus);
objectInfoMap.set(neptune.planet, planetInfo.neptune);
objectInfoMap.set(moon.planet, planetInfo.moon);

// Función para manejar clics en los objetos
function onMouseClick(event: MouseEvent) {
  // Calcular posición normalizada del mouse (-1 a +1)
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

  // Actualizar el raycaster con la posición del mouse y la cámara
  raycaster.setFromCamera(mouse, camera);

  // Lista de objetos seleccionables
  const selectableObjects = [
    sun, mercury.planet, venus.planet, earth.planet, mars.planet,
    jupiter.planet, saturn.planet, uranus.planet, neptune.planet, moon.planet
  ];

  // Verificar intersecciones
  const intersects = raycaster.intersectObjects(selectableObjects, true);

  if (intersects.length > 0) {
    // Encontrar el objeto padre seleccionado (planeta o sol)
    let selectedParent = intersects[0].object;

    // Buscar hacia arriba en la jerarquía para encontrar el objeto padre que está en nuestro mapa
    while (selectedParent && !objectInfoMap.has(selectedParent)) {
      if (selectedParent.parent) {
        selectedParent = selectedParent.parent;
      } else {
        break;
      }
    }

    // Si encontramos un objeto en nuestro mapa
    if (selectedParent && objectInfoMap.has(selectedParent)) {
      selectedObject = selectedParent;
      showInfoPanel(selectedParent);
      focusCamera(selectedParent);
    }
  } else if (selectedObject) {
    // Si hacemos clic fuera de un planeta, ocultar el panel y volver a la vista original
    hideInfoPanel();
    resetCameraPosition();
  }
}

// Función para mostrar el panel de información
function showInfoPanel(object: THREE.Object3D) {
  if (objectInfoMap.has(object)) {
    const info = objectInfoMap.get(object);

    infoPanel.innerHTML = `
      <h2 style="margin-top:0; color:#ffcc00; font-size:18px;">${info.name}</h2>
      <p style="line-height:1.4; margin-bottom:15px;">${info.description}</p>
      <div style="margin-top:10px; padding-top:10px; border-top:1px solid rgba(255,255,255,0.3);">
        <p><strong>Diámetro:</strong> ${info.diameter}</p>
        <p><strong>Distancia al Sol:</strong> ${info.distanceFromSun}</p>
        ${info.distanceFromEarth ? `<p><strong>Distancia a la Tierra:</strong> ${info.distanceFromEarth}</p>` : ''}
        <p><strong>Periodo orbital:</strong> ${info.orbitalPeriod}</p>
        <p><strong>Periodo de rotación:</strong> ${info.rotationPeriod}</p>
        <p><strong>Temperatura:</strong> ${info.temperature}</p>
      </div>
      <div style="text-align:right; margin-top:15px;">
        <button id="closeInfoPanel" style="background:#ff4500; border:none; color:white; padding:5px 10px; border-radius:5px; cursor:pointer;">Cerrar</button>
      </div>
    `;

    infoPanel.style.display = 'block';

    // Añadir evento al botón de cerrar
    document.getElementById('closeInfoPanel')?.addEventListener('click', (e) => {
      e.stopPropagation();
      hideInfoPanel();
      resetCameraPosition();
    });
  }
}

// Función para ocultar el panel de información
function hideInfoPanel() {
  infoPanel.style.display = 'none';
  selectedObject = null;
}

// Función para enfocar la cámara en un objeto
function focusCamera(object: THREE.Object3D) {
  if (cameraAnimationInProgress) return;

  // Guardar la posición actual si aún no se ha guardado
  if (!currentFocusTarget) {
    originalCameraPosition.copy(camera.position);
  }

  currentFocusTarget = object;
  cameraAnimationInProgress = true;

  // Calcular la posición objetivo basada en el objeto
  const objectWorldPosition = new THREE.Vector3();
  object.getWorldPosition(objectWorldPosition);

  // Para objetos como planetas, necesitamos una posición de cámara adecuada
  let targetPosition = new THREE.Vector3();

  // Determinar la distancia basada en el tamaño del objeto
  let distance = 0;

  if (object === sun) {
    distance = 3; // Más cercano para el sol
  } else if (object === jupiter.planet || object === saturn.planet) {
    distance = 2; // Para planetas grandes
  } else {
    distance = 1; // Para planetas pequeños
  }

  // Calcular un ángulo aleatorio para posicionar la cámara (evitamos ver siempre desde el mismo ángulo)
  const angle = Math.PI / 4; // 45 grados, podemos ajustar este valor

  // Calcular la posición objetivo relativa al objeto
  targetPosition.set(
    objectWorldPosition.x + Math.cos(angle) * distance,
    objectWorldPosition.y + 0.5 * distance,
    objectWorldPosition.z + Math.sin(angle) * distance
  );

  // Establecer los controles para que miren al objeto
  controls.target.copy(objectWorldPosition);

  // Animar la transición de la cámara
  const initialPosition = camera.position.clone();
  const duration = 1000; // milisegundos
  const startTime = Date.now();

  function animateCamera() {
    const elapsed = Date.now() - startTime;
    const progress = Math.min(elapsed / duration, 1);

    // Interpolación suave (ease-in-out)
    const t = progress < 0.5
      ? 4 * progress * progress * progress
      : 1 - Math.pow(-2 * progress + 2, 3) / 2;

    camera.position.lerpVectors(initialPosition, targetPosition, t);
    controls.update();

    if (progress < 1) {
      requestAnimationFrame(animateCamera);
    } else {
      cameraAnimationInProgress = false;
    }
  }

  animateCamera();
}

// Función para resetear la cámara a su posición original
function resetCameraPosition() {
  if (cameraAnimationInProgress || !currentFocusTarget) return;

  cameraAnimationInProgress = true;

  // Resetear el target de los controles
  controls.target.set(0, 0, 0);

  // Animar el regreso a la posición original
  const initialPosition = camera.position.clone();
  const targetPosition = originalCameraPosition.clone();
  const duration = 1000; // milisegundos
  const startTime = Date.now();

  function animateCamera() {
    const elapsed = Date.now() - startTime;
    const progress = Math.min(elapsed / duration, 1);

    // Interpolación suave (ease-in-out)
    const t = progress < 0.5
      ? 4 * progress * progress * progress
      : 1 - Math.pow(-2 * progress + 2, 3) / 2;

    camera.position.lerpVectors(initialPosition, targetPosition, t);
    controls.update();

    if (progress < 1) {
      requestAnimationFrame(animateCamera);
    } else {
      currentFocusTarget = null;
      cameraAnimationInProgress = false;
    }
  }

  animateCamera();
}

// Función para manejar el movimiento del mouse y cambiar el cursor
function onMouseMove(event: MouseEvent) {
  // Calcular posición normalizada del mouse (-1 a +1)
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

  // Actualizar el raycaster con la posición del mouse y la cámara
  raycaster.setFromCamera(mouse, camera);

  // Lista de objetos seleccionables
  const selectableObjects = [
    sun, mercury.planet, venus.planet, earth.planet, mars.planet,
    jupiter.planet, saturn.planet, uranus.planet, neptune.planet, moon.planet
  ];

  // Verificar intersecciones
  const intersects = raycaster.intersectObjects(selectableObjects, true);

  if (intersects.length > 0) {
    document.body.style.cursor = 'pointer';
  } else {
    document.body.style.cursor = 'default';
  }
}

// Añadir los eventos al documento
window.addEventListener('click', onMouseClick, false);
window.addEventListener('mousemove', onMouseMove, false);

// Función de manejo de redimensionamiento
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);

  // Si hay un objeto seleccionado, asegurarnos de que el panel de información permanezca visible
  if (selectedObject && objectInfoMap.has(selectedObject)) {
    showInfoPanel(selectedObject);
  }
});

// Función de animación

// ==== Sistema de Meteoritos ====
function createMeteorField(count = 50) {
  const meteors: THREE.Mesh[] = [];
  const meteorGeometry = new THREE.SphereGeometry(0.1, 8, 8);
  const meteorMaterial = new THREE.MeshStandardMaterial({ color: 0xaaaaaa });

  for (let i = 0; i < count; i++) {
    const meteor = new THREE.Mesh(meteorGeometry, meteorMaterial);
    meteor.position.set(
      (Math.random() - 0.5) * 50,
      (Math.random() - 0.5) * 50,
      (Math.random() - 0.5) * 50
    );
    meteor.userData.velocity = new THREE.Vector3(
      (Math.random() - 0.5) * 0.05,
      (Math.random() - 0.5) * 0.05,
      (Math.random() - 0.5) * 0.05
    );
    scene.add(meteor);
    meteors.push(meteor);
  }
  return meteors;
}

const meteors = createMeteorField(80);

function animate() {
  requestAnimationFrame(animate);

  // Actualizar meteoritos
  meteors.forEach(meteor => {
    meteor.position.add(meteor.userData.velocity);
    meteor.rotation.x += 0.01;
    meteor.rotation.y += 0.01;
    // Reposicionar si se aleja demasiado
    if (meteor.position.length() > 60) {
      meteor.position.set(
        (Math.random() - 0.5) * 50,
        (Math.random() - 0.5) * 50,
        (Math.random() - 0.5) * 50
      );
    }
  });


  // Rotación del Sol
  sun.rotation.y += 0.001;

  // Animación suave de las capas del halo solar para dar efecto de corona solar dinámica
  const time = Date.now() * 0.001;
  sunGlow1.scale.set(
    1.0 + Math.sin(time * 0.6) * 0.02,
    1.0 + Math.sin(time * 0.7) * 0.02,
    1.0 + Math.sin(time * 0.8) * 0.02
  );

  // Actualización de los planetas (rotación y órbita)
  // Mercurio
  mercury.planet.rotation.y += mercury.planet.userData.rotationSpeed;
  mercury.orbitContainer.rotation.y += mercury.planet.userData.orbitSpeed;

  // Venus
  venus.planet.rotation.y += venus.planet.userData.rotationSpeed;
  venus.orbitContainer.rotation.y += venus.planet.userData.orbitSpeed;

  // Tierra
  earth.planet.rotation.y += earth.planet.userData.rotationSpeed;
  earth.orbitContainer.rotation.y += earth.planet.userData.orbitSpeed;

  // La Luna rota alrededor de la Tierra
  moon.planet.rotation.y += moon.planet.userData.rotationSpeed;
  moon.planet.position.x = Math.cos(time * moon.planet.userData.orbitSpeed) * moon.planet.userData.distanceFromSun;
  moon.planet.position.z = Math.sin(time * moon.planet.userData.orbitSpeed) * moon.planet.userData.distanceFromSun;

  // Marte
  mars.planet.rotation.y += mars.planet.userData.rotationSpeed;
  mars.orbitContainer.rotation.y += mars.planet.userData.orbitSpeed;

  // Júpiter
  jupiter.planet.rotation.y += jupiter.planet.userData.rotationSpeed;
  jupiter.orbitContainer.rotation.y += jupiter.planet.userData.orbitSpeed;

  // Saturno
  saturn.planet.rotation.y += saturn.planet.userData.rotationSpeed;
  saturn.orbitContainer.rotation.y += saturn.planet.userData.orbitSpeed;

  // Urano
  uranus.planet.rotation.y += uranus.planet.userData.rotationSpeed;
  uranus.orbitContainer.rotation.y += uranus.planet.userData.orbitSpeed;

  // Neptuno
  neptune.planet.rotation.y += neptune.planet.userData.rotationSpeed;
  neptune.orbitContainer.rotation.y += neptune.planet.userData.orbitSpeed;

  // Actualizar la posición de la cámara si hay un objeto seleccionado
  if (currentFocusTarget && !cameraAnimationInProgress) {
    // Obtener la posición mundial actualizada del objeto
    const objectWorldPosition = new THREE.Vector3();
    currentFocusTarget.getWorldPosition(objectWorldPosition);

    // Actualizar el target de los controles para seguir al objeto
    controls.target.copy(objectWorldPosition);

    // Calcular la distancia adecuada basada en el objeto
    let distance = 0;
    if (currentFocusTarget === sun) {
      distance = 3;
    } else if (currentFocusTarget === jupiter.planet || currentFocusTarget === saturn.planet) {
      distance = 2;
    } else {
      distance = 1;
    }

    // Calcular la nueva posición de la cámara relativa al objeto
    // Mantenemos la misma relación/ángulo entre la cámara y el objeto
    const currentOffset = camera.position.clone().sub(controls.target);
    const normalizedOffset = currentOffset.clone().normalize();

    const newCameraPosition = new THREE.Vector3(
      objectWorldPosition.x + normalizedOffset.x * distance,
      objectWorldPosition.y + normalizedOffset.y * distance,
      objectWorldPosition.z + normalizedOffset.z * distance
    );

    // Suavizar el movimiento de la cámara
    camera.position.lerp(newCameraPosition, 0.1);
  }

  // Actualiza los controles de órbita
  controls.update();

  // Renderiza la escena
  renderer.render(scene, camera);
}

// Inicia la animación
animate();