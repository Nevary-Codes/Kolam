let spacing = 60, radius = 30, dots = [], path = [], t = 0;
let rows = 5, cols = 5, shouldDraw = false, canvas;

// === Setup P5 Canvas ===
function setup() {
  canvas = createCanvas(600, 600);
  canvas.parent("kolam-container");
  colorMode(HSB, 360, 100, 100);
  strokeWeight(2);
  noFill();
}

function draw() {
  background(255);
  if (!shouldDraw) return;

  let skipAnimation = document.getElementById("skipAnim").checked;

  // Draw dots
  fill(0); noStroke();
  for (let d of dots) circle(d.x, d.y, 6);

  // Draw path
  noFill();
  for (let i=0; i<(skipAnimation?path.length:int(t)); i++) {
    let p = path[i];
    stroke(p.color);

    if(p.type==="arc"){
      if(p.full) ellipse(p.x,p.y,radius*2,radius*2);
      else arc(p.x,p.y,radius*2,radius*2,p.start,p.end);
    }
    else if(p.type==="line"){ line(p.x1,p.y1,p.x2,p.y2); }
    else if(p.type==="zigzag"){
      beginShape(); for(let pt of p.points) vertex(pt.x, pt.y); endShape();
    }
    else if(p.type==="bezier"){
      bezier(p.x1,p.y1,p.cx1,p.cy1,p.cx2,p.cy2,p.x2,p.y2);
    }
    else if(p.type==="spiral"){
      beginShape();
      for(let a=0; a<p.angles; a+=0.2){
        let r = p.r*(a/p.angles);
        vertex(p.x + cos(a)*r, p.y + sin(a)*r);
      }
      endShape();
    }
  }

  // Draw outline box
  if(document.getElementById("drawBox").checked){
    stroke(document.getElementById("boxColor").value);
    strokeWeight(int(document.getElementById("boxThickness").value));
    noFill();
    rect(20, 20, width-40, height-40, 20);
    strokeWeight(2);
  }

  if(!skipAnimation && t<path.length) t+=0.05;
}

function generateKolam(){
  dots=[]; path=[]; t=0; shouldDraw=true;
  let pattern=document.getElementById("pattern").value;
  let arctype=document.getElementById("arctype").value;
  let lineStyle=document.getElementById("lineStyle").value;
  let interconnected=document.getElementById("interconnected").checked;
  rows=int(document.getElementById("rows").value);
  cols=int(document.getElementById("cols").value);
  radius=int(document.getElementById("radius").value);
  let baseColor=document.getElementById("baseColor").value;

  if(pattern==="classic"||pattern==="flower") generateGridPattern(pattern);
  else if(pattern==="diamond") generateDiamondPattern();
  else if(pattern==="radialcircle") generateRadialPattern(arctype, baseColor);

  if(lineStyle==="arcs"){
    if(pattern==="classic"||pattern==="flower") generatePathClassic(arctype, baseColor);
    if(pattern==="diamond") generatePathDiamond(arctype, baseColor);
  } else generateLineBasedPath(lineStyle, interconnected, baseColor);
}

function clearKolam(){ shouldDraw=false; background(255); }

// === Grid & Pattern Generators ===
function generateGridPattern(pattern){
  let offsetX=width/2-(cols-1)*spacing/2;
  let offsetY=height/2-(rows-1)*spacing/2;
  if(pattern==="classic"){
    for(let r=0;r<rows;r++) for(let c=0;c<cols;c++)
      dots.push({x:offsetX+c*spacing,y:offsetY+r*spacing,row:r,col:c,layer:r});
  } else if(pattern==="flower"){
    let centerX=width/2, centerY=height/2;
    let layers=Math.min(rows,cols);
    for(let r=0;r<layers;r++) for(let c=0;c<layers;c++)
      if((r+c)%2===0){
        let x=centerX+(c-layers/2)*spacing;
        let y=centerY+(r-layers/2)*spacing;
        dots.push({x,y,row:r,col:c,layer:r});
      }
  }
}

function generateDiamondPattern(){
  let centerX=width/2, centerY=height/2; dots=[];
  for(let r=-rows+1;r<rows;r++)
    for(let c=-cols+1;c<cols;c++)
      if(Math.abs(r+c)%2===0){
        let x=centerX+c*spacing, y=centerY+r*spacing;
        dots.push({x,y,row:r,col:c,layer:Math.abs(r)});
      }
}

function generatePathClassic(arctype, baseColor){
  for(let r=0;r<rows;r++){
    let leftToRight=r%2===0;
    for(let c=leftToRight?0:cols-1; leftToRight?c<cols:c>=0; leftToRight?c++:c--){
      let dot=dots[r*cols+c]||dots[0];
      let color=colorCycle(dot.layer, baseColor);
      if(arctype==="full") path.push({type:"arc",x:dot.x,y:dot.y,full:true,color});
      else{
        if((r+c)%2===0){
          path.push({type:"arc",x:dot.x,y:dot.y,start:0,end:HALF_PI,color});
          path.push({type:"arc",x:dot.x,y:dot.y,start:PI,end:PI+HALF_PI,color});
        } else{
          path.push({type:"arc",x:dot.x,y:dot.y,start:HALF_PI,end:PI,color});
          path.push({type:"arc",x:dot.x,y:dot.y,start:PI+HALF_PI,end:TWO_PI,color});
        }
      }
    }
  }
}

function generatePathDiamond(arctype, baseColor){
  let sortedDots=dots.slice().sort((a,b)=>a.y-b.y||a.x-b.x);
  let currentY=null, rowDots=[];
  for(let dot of sortedDots){
    if(currentY===null||Math.abs(dot.y-currentY)<1){rowDots.push(dot); currentY=dot.y;}
    else{ addRowToPath(rowDots,arctype,baseColor); rowDots=[dot]; currentY=dot.y;}
  }
  if(rowDots.length>0) addRowToPath(rowDots,arctype,baseColor);
}

function addRowToPath(rowDots,arctype,baseColor){
  for(let i=0;i<rowDots.length;i++){
    let dot=rowDots[i]; let color=colorCycle(dot.layer, baseColor);
    if(arctype==="full") path.push({type:"arc",x:dot.x,y:dot.y,full:true,color});
    else{
      if(i%2===0){
        path.push({type:"arc",x:dot.x,y:dot.y,start:0,end:HALF_PI,color});
        path.push({type:"arc",x:dot.x,y:dot.y,start:PI,end:PI+HALF_PI,color});
      } else {
        path.push({type:"arc",x:dot.x,y:dot.y,start:HALF_PI,end:PI,color});
        path.push({type:"arc",x:dot.x,y:dot.y,start:PI+HALF_PI,end:TWO_PI,color});
      }
    }
  }
}

// === Line & Shape Paths ===
function generateLineBasedPath(lineStyle, interconnected, baseColor){
  if(interconnected){
    for(let i=0;i<dots.length-1;i++){
      let d1=dots[i], d2=dots[i+1];
      let color=colorCycle(d1.layer, baseColor);
      if(lineStyle==="zigzag"){
        let midX=(d1.x+d2.x)/2, midY=(d1.y+d2.y)/2;
        path.push({type:"zigzag",points:[{x:d1.x,y:d1.y},{x:midX+10,y:midY-10},{x:d2.x,y:d2.y}],color});
      }
      else if(lineStyle==="bezier"){
        let cx1=d1.x+random(-30,30), cy1=d1.y+random(-30,30);
        let cx2=d2.x+random(-30,30), cy2=d2.y+random(-30,30);
        path.push({type:"bezier",x1:d1.x,y1:d1.y,cx1,cy1,cx2,cy2,x2:d2.x,y2:d2.y,color});
      }
      else if(lineStyle==="spiral"){
        path.push({type:"spiral",x:d1.x,y:d1.y,r:radius,angles:TWO_PI*2,color});
      }
    }
  } else {
    for(let d of dots){
      let color=colorCycle(d.layer, baseColor);
      if(lineStyle==="zigzag")
        path.push({type:"zigzag",points:[{x:d.x-radius,y:d.y},{x:d.x,y:d.y-radius},{x:d.x+radius,y:d.y}],color});
      else if(lineStyle==="bezier")
        path.push({type:"bezier",x1:d.x-radius,y1:d.y,x2:d.x+radius,y2:d.y,cx1:d.x,cy1:d.y-radius*2,cx2:d.x,cy2:d.y+radius*2,color});
      else if(lineStyle==="spiral")
        path.push({type:"spiral",x:d.x,y:d.y,r:radius,angles:TWO_PI*2,color});
    }
  }
}

function generateRadialPattern(arctype, baseColor){
  let centerX=width/2, centerY=height/2;
  let layers=Math.min(rows,cols);
  for(let r=0;r<layers;r++){
    let numDots=r*6+6, radiusLayer=spacing*(r+1);
    for(let i=0;i<numDots;i++){
      let angle=TWO_PI*i/numDots;
      let x=centerX+radiusLayer*cos(angle);
      let y=centerY+radiusLayer*sin(angle);
      dots.push({x,y,row:r,col:i,layer:r});
    }
  }
}

function colorCycle(layer, base){
  let c=color(base); let h=hue(c), s=saturation(c), b=brightness(c);
  return color((h+layer*15)%360,s,b);
}