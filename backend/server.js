const express = require('express');
const cors = require('cors');
const admin = require('firebase-admin');
const serviceAccount = require('./serviceAccountKey.json');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json());


admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

const db = admin.firestore();

app.post('/api/poids', async (req, res) => {
  const { name, weight } = req.body;
  if (!name || weight === undefined) {
    return res.status(400).send("Nom ou poids manquant");
  }

  try {
    await db.collection('produits').add({
      name,
      weight,
      timestamp: new Date()
    });
    res.send("Données enregistrées");
  } catch (err) {
    console.error(err);
    res.status(500).send("Erreur Firestore");
  }
});

let currentCommande = { start: false, name: null };


app.get('/api/commande', (req, res) => {
  res.json(currentCommande);
});

app.post('/api/commande', (req, res) => {
  const { start, name } = req.body;
  currentCommande = { start, name };

  res.send("Commande mise à jour");
});

app.get('/api/produits', async (req, res) => {
  const snapshot = await db.collection("produits").get();
  const produits = snapshot.docs.map(doc => doc.data());
  res.json(produits);
});

app.listen(3000, "0.0.0.0", () => {
  console.log('Serveur démarré sur http://localhost:3000');
});