const S = 10, R = 28, B = 8 / 3, DT = 0.005;
function step(a){const[x,y,z]=a,h=DT;const f=(x,y,z)=>[S*(y-x),x*(R-z)-y,x*y-B*z];
 const k1=f(x,y,z),k2=f(x+.5*h*k1[0],y+.5*h*k1[1],z+.5*h*k1[2]),k3=f(x+.5*h*k2[0],y+.5*h*k2[1],z+.5*h*k2[2]),k4=f(x+h*k3[0],y+h*k3[1],z+h*k3[2]);
 for(let i=0;i<3;i++)a[i]+=h/6*(k1[i]+2*k2[i]+2*k3[i]+k4[i]);}
let p=[1,1,1];for(let i=0;i<4000;i++)step(p);
let a=p.slice(),b=[p[0]+1e-9,p[1],p[2]];
let k1=-1,iv=[],cur=null;
for(let k=1;k<=18000;k++){step(a);step(b);const d=Math.hypot(a[0]-b[0],a[1]-b[1],a[2]-b[2]);
 if(k1<0&&d>1)k1=k; if(k1<0)continue;
 const opp=Math.sign(a[0])!==Math.sign(b[0]);
 if(opp&&cur===null)cur=k; if(!opp&&cur!==null){iv.push([cur*DT,(k-cur)*DT]);cur=null;}}
console.log('distance>1 at',k1*DT);
console.log('opposite-wing intervals (start, length) in sim units:');
console.log(iv.map(([s,l])=>`${s.toFixed(2)}:${l.toFixed(2)}`).join('  '));
