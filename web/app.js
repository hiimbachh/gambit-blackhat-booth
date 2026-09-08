import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
const $=id=>document.getElementById(id),stage=$('stage');
const scene=new THREE.Scene();scene.background=new THREE.Color('#e9e6e3');
const camera=new THREE.PerspectiveCamera(40,1,.05,200);
let renderer;
try{renderer=new THREE.WebGLRenderer({antialias:true});}catch(e){$('status').textContent='3D rendering is unavailable. Please enable browser hardware acceleration.';throw e;}
renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;stage.append(renderer.domElement);
renderer.domElement.setAttribute('aria-label','Gambit booth 3D canvas');
const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.autoRotateSpeed=.7;controls.maxPolarAngle=Math.PI*.49;controls.minDistance=2;controls.maxDistance=45;
const pmrem=new THREE.PMREMGenerator(renderer),room=new RoomEnvironment();scene.environment=pmrem.fromScene(room,.04).texture;room.dispose();pmrem.dispose();scene.environmentIntensity=.65;
const key=new THREE.DirectionalLight(0xfff1e6,3);key.position.set(8,12,8);key.castShadow=true;key.shadow.mapSize.set(2048,2048);Object.assign(key.shadow.camera,{left:-12,right:12,top:12,bottom:-12,near:.1,far:50});key.shadow.bias=-.0002;key.shadow.normalBias=.025;scene.add(key,key.target);scene.add(new THREE.HemisphereLight(0xe7eeff,0x7b6574,1.2));
let model,center=new THREE.Vector3(),size=new THREE.Vector3(),materials=[],roofs=[],videos=[],currentView=0;
const original=new Map(),wire=new THREE.MeshBasicMaterial({color:0x67364f,wireframe:true});
const views=[[1,.30,1],[-1,.28,1],[1,.30,-1],[1,.06,1]];
function view(index){if(!model)return;currentView=index;const roof=index===3;const target=center.clone();if(roof)target.y+=size.y*.24;const vertical=THREE.MathUtils.degToRad(camera.fov);const horizontal=2*Math.atan(Math.tan(vertical/2)*camera.aspect);const distance=(roof?size.y*.42:Math.max(size.x,size.y,size.z)*.75)/Math.tan(Math.min(vertical,horizontal)/2);camera.position.copy(target).add(new THREE.Vector3(...views[index]).normalize().multiplyScalar(distance));controls.target.copy(target);controls.update();document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',Number(b.dataset.view)===index));}
function resize(){const w=stage.clientWidth,h=stage.clientHeight;renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();}new ResizeObserver(resize).observe(stage);resize();
function apply(){renderer.toneMappingExposure=+$('exposure').value;key.intensity=3*+$('light').value;const a=THREE.MathUtils.degToRad(+$('angle').value);key.position.set(Math.cos(a)*12,12,Math.sin(a)*12);camera.fov=+$('fov').value;camera.updateProjectionMatrix();controls.autoRotate=$('orbit').checked;for(const o of roofs)o.position.y=o.userData.baseY+Number($('roof').value)*o.userData.tier;for(const [id,suffix,digits] of [['exposure','',1],['light','',1],['angle','°',0],['roof',' m',2],['fov','°',0]])$(id+'-value').value=Number($(id).value).toFixed(digits)+suffix;}
for(const id of ['exposure','light','angle','roof','fov','orbit'])$(id).addEventListener('input',apply);
$('wire').addEventListener('change',()=>{for(const [mesh,mat] of original)mesh.material=$('wire').checked?wire:mat;$('mode').textContent=$('wire').checked?'Wireframe · mesh structure':'Realistic materials & lighting';});
async function play(){const results=await Promise.allSettled(videos.map(v=>$('play').checked?v.play():v.pause()));$('media-status').textContent=results.some(r=>r.status==='rejected')?'Enable Play screens to start video playback.':$('play').checked?'Screen loops playing':'Screen loops paused';}
$('play').addEventListener('change',play);
$('reset').addEventListener('click',()=>{for(const [id,val] of Object.entries({exposure:1,light:1,angle:45,roof:0,fov:40}))$(id).value=val;$('orbit').checked=false;$('wire').checked=false;$('play').checked=true;for(const [mesh,mat] of original)mesh.material=mat;$('mode').textContent='Realistic materials & lighting';apply();view(0);play();});
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>view(Number(b.dataset.view))));
async function init(){
 const [gltf,mapping]=await Promise.all([new GLTFLoader().loadAsync('./booth.glb'),fetch('./media.json').then(r=>{if(!r.ok)throw Error('Media mapping missing');return r.json();})]);
 model=gltf.scene;scene.add(model);model.updateMatrixWorld(true);const box=new THREE.Box3();model.traverse(o=>{if(o.isMesh&&!/floor|ground|cable|suspension/i.test(o.name))box.expandByObject(o);});box.getCenter(center);box.getSize(size);
 model.traverse(o=>{if(o.isLight)o.visible=false;if(o.isMesh){o.castShadow=true;o.receiveShadow=true;original.set(o,o.material);materials.push(...(Array.isArray(o.material)?o.material:[o.material]));}if(o.name.startsWith('ROOF_L')){o.userData.baseY=o.position.y;o.userData.tier=Number(o.name.match(/ROOF_L(\d)/)?.[1]||1);roofs.push(o);}});
 const cache=new Map();let count=0;
 for(const material of new Set(materials)){const entry=mapping[material.name];if(!entry)continue;let texture=cache.get(entry.url);if(!texture){const video=document.createElement('video');video.src=entry.url;video.muted=true;video.loop=true;video.playsInline=true;video.preload='auto';video.addEventListener('error',()=>{$('media-status').textContent='A screen clip could not load. Check the media folder.';});videos.push(video);texture=new THREE.VideoTexture(video);texture.colorSpace=THREE.SRGBColorSpace;texture.flipY=false;cache.set(entry.url,texture);}material.map=texture;material.color.set(0xffffff);material.emissive?.set(0xffffff);material.emissiveMap=texture;material.emissiveIntensity=.7;material.needsUpdate=true;count++;}
 $('controls').disabled=false;$('status').hidden=true;apply();view(0);await play();console.info(`Loaded ${original.size} meshes, ${count} video materials, ${roofs.length} roof blocks`);
}
init().catch(e=>{console.error(e);$('status').hidden=false;$('status').textContent='Could not load the booth. Start the local server and check that booth.glb, media.json and vendor files are present.';});
renderer.setAnimationLoop(()=>{controls.update();renderer.render(scene,camera);});
