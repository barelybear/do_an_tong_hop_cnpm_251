export default async function callPython({ function_name, args }) {
  console.log("🔹 About to call Python backend...");
  
  try {
    const res = await fetch("http://127.0.0.1:5000/api/process", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ function_name, args })
    });
    console.log("🔹 Fetch finished, got response:", res);
    
    const data = await res.json();
    console.log("Python output:", data.output);
    return data;
  } catch (err) {
    console.error("❌ Fetch failed:", err);
  }
}
