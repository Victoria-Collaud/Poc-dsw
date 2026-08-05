import swaggerUi from "swagger-ui-express"; // YAML
import YAML from "yamljs";
import express from "express";

const app = express();
const PORT = 3000;
const swaggerDocument = YAML.load("./openapi.yaml");
app.use(express.json());

// Datos de ejemplo
let movies = [
  { id: 1, titulo: "Avatar", director: "James Cameron" },
  { id: 2, titulo: "Titanic", director: "James Cameron" }
];

// GET - Obtener todas las películas
app.get("/movies", (req, res) => {
  res.json(movies);
});

// GET - Obtener una película por ID
app.get("/movies/:id", (req, res) => {
  const movie = movies.find(m => m.id == req.params.id);

  if (!movie) {
    return res.status(404).json({ mensaje: "Película no encontrada" });
  }

  res.json(movie);
});

// POST - Agregar una película
app.post("/movies", (req, res) => {
  const nueva = {
    id: movies.length + 1,
    titulo: req.body.titulo,
    director: req.body.director
  };

  movies.push(nueva);

  res.status(201).json(nueva);
});

// PUT - Modificar una película
app.put("/movies/:id", (req, res) => {
  const movie = movies.find(m => m.id == req.params.id);

  if (!movie) {
    return res.status(404).json({ mensaje: "Película no encontrada" });
  }

  movie.titulo = req.body.titulo;
  movie.director = req.body.director;

  res.json(movie);
});

// DELETE - Eliminar una película
app.delete("/movies/:id", (req, res) => {
  movies = movies.filter(m => m.id != req.params.id);

  res.json({ mensaje: "Película eliminada" });
});
app.use("/api-docs", swaggerUi.serve, swaggerUi.setup(swaggerDocument)); //YALM
app.listen(PORT, () => {
  console.log(`Servidor ejecutándose en http://localhost:${PORT}`);
});