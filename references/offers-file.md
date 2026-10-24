# Offers file format

Save the confirmed offers to `~/.config/gapquest/last_offers.json` (create the folder if needed) and pass
it to `scripts/compare.py --offers`.

```json
{
  "item": "AirPods Pro 2 (USB-C)",
  "offers": [
    {"seller": "Best Buy", "price": 189.99, "shipping": 0, "pickup": true, "condition": "new", "url": "https://..."},
    {"seller": "Apple Education", "price": 249.00, "discount_percent": 10, "discount_note": "student pricing", "condition": "new", "url": "https://..."},
    {"seller": "Back Market", "price": 149.00, "shipping": 5.99, "condition": "refurbished, 1-year warranty", "url": "https://..."},
    {"seller": "Facebook Marketplace, Tempe", "price": 120.00, "taxed": false, "condition": "used, like new", "pickup": true, "url": "https://..."}
  ]
}
```

- `seller` and `price` are required. `price` is the listed price before discounts, tax and shipping.
- `discount` (dollars) and/or `discount_percent`: only a coupon or student discount you confirmed applies;
  `discount_note` says which.
- `shipping`: dollars; 0 or leave out for free shipping or pickup.
- `taxed`: `false` for private sales (marketplace listings) where no sales tax is charged. Default `true`.
- `condition`: `new` unless it is used, refurbished or open box; include the warranty if any.
- `pickup`: `true` when it can be picked up locally.
