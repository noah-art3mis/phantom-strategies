import * as THREE from "three";

// An interference-colored membrane, deformed in 3D like a folded soap film.
export function createScene(container, initiallyPaused) {
  const renderer = new THREE.WebGLRenderer({
    alpha: true,
    antialias: true,
    powerPreference: "low-power",
  });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
  container.appendChild(renderer.domElement);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(35, 1, 0.1, 100);
  camera.position.z = 5.8;
  const material = new THREE.ShaderMaterial({
    uniforms: { uTime: { value: 0 }, uIntensity: { value: 0 } },
    transparent: true,
    side: THREE.DoubleSide,
    depthWrite: false,
    vertexShader: `
      uniform float uTime;
      varying vec3 vNormal;
      varying vec3 vPosition;
      varying vec3 vView;
      void main() {
        vec3 p = position;
        float wave = sin(p.y * 4.0 + uTime * .32) * cos(p.x * 3.0 - uTime * .18);
        p += normal * wave * .16;
        float twist = p.y * .7 + sin(uTime * .12) * .2;
        p.xz = mat2(cos(twist), -sin(twist), sin(twist), cos(twist)) * p.xz;
        vec4 mv = modelViewMatrix * vec4(p, 1.0);
        vNormal = normalize(normalMatrix * normal);
        vView = normalize(-mv.xyz);
        vPosition = p;
        gl_Position = projectionMatrix * mv;
      }
    `,
    fragmentShader: `
      uniform float uTime;
      uniform float uIntensity;
      varying vec3 vNormal;
      varying vec3 vPosition;
      varying vec3 vView;
      void main() {
        vec3 n = normalize(vNormal);
        float facing = abs(dot(n, normalize(vView)));
        float rim = pow(1.0 - facing, 2.1);
        float bands = dot(vPosition, vec3(.5,.65,.3)) + facing * 1.2 + uTime * .018;
        vec3 rainbow = .52 + .48 * cos(6.28318 * (bands + vec3(0.,.33,.67)));
        float fine = pow(.5 + .5 * sin(vPosition.y * 70.0 + vPosition.x * 18.0), 24.0);
        float lighting = pow(max(dot(n, normalize(vec3(-.3,.8,1.))), 0.), 18.0);
        vec3 color = rainbow * (.32 + rim * 1.3) + vec3(.75,.85,.9) * lighting * .8;
        color += fine * rim * .16 + uIntensity * .1;
        gl_FragColor = vec4(color, .15 + rim * .7 + lighting * .2);
      }
    `,
  });
  const geometry = new THREE.TorusKnotGeometry(1.06, 0.33, 260, 40, 2, 3);
  const apparition = new THREE.Mesh(geometry, material);
  apparition.rotation.set(0.5, -0.4, -0.4);
  apparition.scale.set(1.05, 1.22, 0.8);
  scene.add(apparition);
  let paused = initiallyPaused;
  let visible = true;
  let listening = false;
  let time = 0;
  let previous = 0;
  const pointer = new THREE.Vector2();
  function render(timestamp = 0) {
    const delta = previous ? Math.min((timestamp - previous) / 1000, 0.05) : 0;
    previous = timestamp;
    time += delta;
    material.uniforms.uTime.value = time;
    material.uniforms.uIntensity.value +=
      ((listening ? 1 : 0) - material.uniforms.uIntensity.value) * 0.025;
    apparition.rotation.y = -0.4 + time * 0.075 + pointer.x * 0.015;
    apparition.rotation.x =
      0.5 + Math.sin(time * 0.12) * 0.15 + pointer.y * 0.01;
    renderer.render(scene, camera);
  }
  function updateLoop() {
    previous = 0;
    renderer.setAnimationLoop(
      !paused && visible && !document.hidden ? render : null,
    );
    if (paused) renderer.render(scene, camera);
  }
  const resize = new ResizeObserver(() => {
    const { width, height } = container.getBoundingClientRect();
    if (!width || !height) return;
    renderer.setSize(width, height);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.render(scene, camera);
  });
  resize.observe(container);
  const intersection = new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting;
    updateLoop();
  });
  intersection.observe(container);
  const move = (event) => {
    pointer.set(
      event.clientX / innerWidth - 0.5,
      event.clientY / innerHeight - 0.5,
    );
  };
  window.addEventListener("pointermove", move, { passive: true });
  document.addEventListener("visibilitychange", updateLoop);
  const lost = (event) => {
    event.preventDefault();
    renderer.setAnimationLoop(null);
    renderer.domElement.hidden = true;
  };
  renderer.domElement.addEventListener("webglcontextlost", lost);
  updateLoop();
  return {
    setPaused(value) {
      paused = value;
      updateLoop();
    },
    setListening(value) {
      listening = value;
    },
    dispose() {
      renderer.setAnimationLoop(null);
      resize.disconnect();
      intersection.disconnect();
      window.removeEventListener("pointermove", move);
      document.removeEventListener("visibilitychange", updateLoop);
      renderer.domElement.removeEventListener("webglcontextlost", lost);
      geometry.dispose();
      material.dispose();
      renderer.dispose();
      renderer.domElement.remove();
    },
  };
}
