interface Address {
  street?: string;
  city?: string;
  state?: string;
  zipCode?: string;
}

export function parseAddress(formattedAddress?: string | null): Address {
  const address: Address = {};
  if (formattedAddress) {
    const addressParts = formattedAddress.split(", ");
    address.street = addressParts[0];
    address.city = addressParts[1];
    address.state = addressParts[2];
    address.zipCode = addressParts[3];
  }
  return address;
}
