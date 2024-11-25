import{ag as m,a3 as L,ah as I,z as C,v as P,Y as z,ad as K,K as x,x as Y,L as G,ai as J,o as g,aj as j,ak as k,V as y,C as N,B as v,y as B,al as A,am as R,q as Q,an as U,ao as X,ap as Z,aq as ee,ar as re,as as te,N as ae,p as ne,j as se,c as ie,n as D,b as ue,aa as oe,g as fe,H as ce}from"./runtime.Cw8BEO9w.js";import{d as le}from"./disclose-version.asnYb6NB.js";let V=!1;function de(){V||(V=!0,document.addEventListener("reset",e=>{Promise.resolve().then(()=>{var r;if(!e.defaultPrevented)for(const a of e.target.elements)(r=a.__on_r)==null||r.call(a)})},{capture:!0}))}function M(e){var r=I,a=C;m(null),L(null);try{return e()}finally{m(r),L(a)}}function Te(e,r,a,n=a){e.addEventListener(r,()=>M(a));const s=e.__on_r;s?e.__on_r=()=>{s(),n()}:e.__on_r=n,de()}const _e=new Set,q=new Set;function he(e,r,a,n){function s(t){if(n.capture||w.call(r,t),!t.cancelBubble)return M(()=>a.call(this,t))}return e.startsWith("pointer")||e.startsWith("touch")||e==="wheel"?z(()=>{r.addEventListener(e,s,n)}):r.addEventListener(e,s,n),s}function me(e,r,a,n,s){var t={capture:n,passive:s},f=he(e,r,a,t);(r===document.body||r===window||r===document)&&P(()=>{r.removeEventListener(e,f,t)})}function w(e){var H;var r=this,a=r.ownerDocument,n=e.type,s=((H=e.composedPath)==null?void 0:H.call(e))||[],t=s[0]||e.target,f=0,p=e.__root;if(p){var d=s.indexOf(p);if(d!==-1&&(r===document||r===window)){e.__root=r;return}var _=s.indexOf(r);if(_===-1)return;d<=_&&(f=d)}if(t=s[f]||e.target,t!==r){K(e,"currentTarget",{configurable:!0,get(){return t||a}});var S=I,c=C;m(null),L(null);try{for(var i,u=[];t!==null;){var l=t.assignedSlot||t.parentNode||t.host||null;try{var h=t["__"+n];if(h!==void 0&&!t.disabled)if(x(h)){var[F,...$]=h;F.apply(t,[e,...$])}else h.call(t,e)}catch(E){i?u.push(E):i=E}if(e.cancelBubble||l===r||l===null)break;t=l}if(i){for(let E of u)queueMicrotask(()=>{throw E});throw i}}finally{e.__root=r,delete e.currentTarget,m(S),L(c)}}}let o;function ve(){o=void 0}function Le(e){let r=null,a=g;var n;if(g){for(r=v,o===void 0&&(o=B(document.head));o!==null&&(o.nodeType!==8||o.data!==j);)o=k(o);o===null?y(!1):o=N(k(o))}g||(n=document.head.appendChild(Y()));try{G(()=>e(n),J)}finally{a&&(y(!0),o=v,N(r))}}const pe=["touchstart","touchmove"];function be(e){return pe.includes(e)}function Ne(e,r){var a=r==null?"":typeof r=="object"?r+"":r;a!==(e.__t??(e.__t=e.nodeValue))&&(e.__t=a,e.nodeValue=a==null?"":a+"")}function ye(e,r){return W(e,r)}function Se(e,r){A(),r.intro=r.intro??!1;const a=r.target,n=g,s=v;try{for(var t=B(a);t&&(t.nodeType!==8||t.data!==j);)t=k(t);if(!t)throw R;y(!0),N(t),Q();const f=W(e,{...r,anchor:t});if(v===null||v.nodeType!==8||v.data!==U)throw X(),R;return y(!1),f}catch(f){if(f===R)return r.recover===!1&&Z(),A(),ee(a),y(!1),ye(e,r);throw f}finally{y(n),N(s),ve()}}const b=new Map;function W(e,{target:r,anchor:a,props:n={},events:s,context:t,intro:f=!0}){A();var p=new Set,d=c=>{for(var i=0;i<c.length;i++){var u=c[i];if(!p.has(u)){p.add(u);var l=be(u);r.addEventListener(u,w,{passive:l});var h=b.get(u);h===void 0?(document.addEventListener(u,w,{passive:l}),b.set(u,1)):b.set(u,h+1)}}};d(re(_e)),q.add(d);var _=void 0,S=te(()=>{var c=a??r.appendChild(Y());return ae(()=>{if(t){ne({});var i=ie;i.c=t}s&&(n.$$events=s),g&&le(c,null),_=e(c,n)||{},g&&(C.nodes_end=v),t&&se()}),()=>{var l;for(var i of p){r.removeEventListener(i,w);var u=b.get(i);--u===0?(document.removeEventListener(i,w),b.delete(i)):b.set(i,u)}q.delete(d),O.delete(_),c!==a&&((l=c.parentNode)==null||l.removeChild(c))}});return O.set(_,S),_}let O=new WeakMap;function Re(e){const r=O.get(e);r&&r()}function ge(e,r,a){if(e==null)return r(void 0),D;const n=ue(()=>e.subscribe(r,a));return n.unsubscribe?()=>n.unsubscribe():n}let T=!1;function ke(e,r,a){const n=a[r]??(a[r]={store:null,source:oe(void 0),unsubscribe:D});if(n.store!==e)if(n.unsubscribe(),n.store=e??null,e==null)n.source.v=void 0,n.unsubscribe=D;else{var s=!0;n.unsubscribe=ge(e,t=>{s?n.source.v=t:ce(n.source,t)}),s=!1}return fe(n.source)}function Ae(){const e={};return P(()=>{for(var r in e)e[r].unsubscribe()}),e}function De(e){var r=T;try{return T=!1,[e(),T]}finally{T=r}}export{Ne as a,ke as b,De as c,de as d,me as e,Le as f,Se as h,Te as l,ye as m,Ae as s,Re as u};
