const mongoose = require('mongoose');

// Define Order schema
const OrderSchema = new mongoose.Schema({
  productId: { type: mongoose.Schema.Types.ObjectId, ref: 'Product', required: true },
  quantity: { type: Number, required: true },
  totalAmount: { type: Number, required: true },
  orderDate: { type: Date, default: Date.now },
});

// Create the Order model
const Order = mongoose.model('Order', OrderSchema);

module.exports = Order;
