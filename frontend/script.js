  function table(reponse){
    let table = '';

    table += '<tr><td>'+ reponse.name +'</td><td>'+ reponse.weight+'</td></tr>';

    document.getElementById("tableBody").innerHTML += table;
}
  /*
document.addEventListener("DOMContentLoaded", async function () {
    try {
      const res = await fetch("http://192.168.1.45:3000/api/produits");
      const produits = await res.json();
      produits.forEach(p => table(p));
    } catch (err) {
      console.error("Erreur lors du chargement des produits", err);
    }
});*/
async function chargerProduits() {
  try {
    const res = await fetch("http://192.168.1.45:3000/api/produits");
    const produits = await res.json();
    document.getElementById("tableBody").innerHTML = ""; 
    produits.forEach(p => table(p));
  } catch (err) {
    console.error("Erreur lors du chargement des produits", err);
  }
} 
  
async function peser(){
    const nom = document.getElementById("nom").value.trim();
    
    if (!nom){
      alert("Veuillez entrer un nom !");
      return;
    }
  
    try {
      await fetch("http://192.168.1.45:3000/api/commande", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ start: true, name: nom})
      });
      
      setTimeout(() => {
        chargerProduits(); // recharge la table
      }, 3000);
  
    }
    catch (error) {
      console.error("Erreur", error)
      alert("Erreur lors de l'envoi");
    }
}
  