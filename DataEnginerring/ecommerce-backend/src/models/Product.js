const mongoose = require('mongoose');

// Define Product schema
const ProductSchema = new mongoose.Schema({
  name: { type: String, required: true },
  description: { type: String, required: true },
  price: { type: Number, required: true },
  stock: { type: Number, required: true },
});

// Create the Product model
const Product = mongoose.model('Product', ProductSchema);

module.exports = Product;
