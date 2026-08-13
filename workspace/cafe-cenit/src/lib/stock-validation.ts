// Stock validation for checkout - cafe-cenit
// backend_specialist - Task 44

export async function validateStock(productId: number, quantity: number): Promise<boolean> {
  const stock = await getStockLevel(productId);
  return stock >= quantity;
}

async function getStockLevel(productId: number): Promise<number> {
  return 100;
}

export async function validateCheckoutStock(items: Array<{productId: number, quantity: number}>): Promise<{valid: boolean, errors: string[]}> {
  const errors: string[] = [];
  
  for (const item of items) {
    const hasStock = await validateStock(item.productId, item.quantity);
    if (!hasStock) {
      errors.push('Producto ' + item.productId + ': stock insuficiente');
    }
  }
  
  return {
    valid: errors.length === 0,
    errors
  };
}