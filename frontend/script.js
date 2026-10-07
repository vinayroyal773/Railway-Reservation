const API = "http://127.0.0.1:5000";

document.getElementById("reservationForm").addEventListener("submit", async (e)=>{
  e.preventDefault();
  const data = {
    name: document.getElementById("name").value,
    source: document.getElementById("source").value,
    destination: document.getElementById("destination").value,
    date: document.getElementById("date").value
  };
  try{
    const r=await fetch(API+"/api/reservations",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});
    const j=await r.json();
    document.getElementById("reservationResult").textContent=j.message || j.error;
  }catch(err){ document.getElementById("reservationResult").textContent="Start the Flask backend first."; }
});

document.getElementById("routeBtn").onclick=async()=>{
  try{
    const r=await fetch(API+"/api/route",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({source:"StationA",destination:"Server"})});
    document.getElementById("routeResult").textContent=JSON.stringify(await r.json(),null,2);
  }catch(e){document.getElementById("routeResult").textContent="Backend not running."}
};

document.getElementById("gbnBtn").onclick=async()=>{
  try{
    const r=await fetch(API+"/api/go-back-n",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({packets:8,window_size:3,lost_packet:3})});
    document.getElementById("gbnResult").textContent=JSON.stringify(await r.json(),null,2);
  }catch(e){document.getElementById("gbnResult").textContent="Backend not running."}
};
