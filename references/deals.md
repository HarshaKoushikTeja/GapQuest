# GapQuest mode: Deal Finder

Read this when the student's request matches this mode (see the Modes table in SKILL.md). Commands run from the GapQuest folder. The Replies and asking-first rules in SKILL.md apply here too.

A student is about to pay full price for headphones, a textbook or a calculator. This Skill checks the places
students actually save money (student pricing, used and refurbished, local pickup, coupons) and compares the real
total, not the sticker price.

## When to use

- "Where can I get AirPods Pro cheapest?"
- [product link or screenshot] "Is this a good price?"
- "Need the textbook for ECN 211, ISBN 978..., cheapest?"
- "Any student discount on a new laptop?"

Do not use it for groceries, food delivery (food delivery and late-night food are the food-run mode, references/food-run.md), or anything illegal or age-restricted.

## Steps

1. **Pin down the exact item.** From the student's text, link, photo or screenshot, identify the exact product:
   brand, model, size or storage, color if it changes the price, and the ISBN for textbooks (the edition matters).
   If two models are plausible, ask one short question ("AirPods Pro 2 with USB-C?"). Ask whether used or
   refurbished is OK only if it would change the answer; default to "new, and show used separately".

2. **Know the student.** Use what Cubbie remembers: city or campus (for local pickup and sales tax), whether they
   have Amazon Prime Student or other memberships, and their budget. Ask only what this search needs and remember it.

3. **Search wide, with Cubbie's web ability.** Check, as relevant to the item:
   - Major retailers: Amazon, Walmart, Target, Best Buy, the brand's own store, Costco if they're a member.
   - Student pricing: the brand's education store (Apple, Samsung, Microsoft, Dell, Lenovo, HP), student programs such
     as UNiDAYS and Student Beans, Amazon Prime Student, and the campus bookstore or tech store.
   - Used and refurbished: Back Market, eBay (seller rating 98%+), Amazon Renewed, manufacturer refurbished stores.
     Label condition and warranty clearly.
   - Textbooks: rental and used sites (for example Chegg, Amazon rental, AbeBooks, BookFinder), the campus bookstore,
     the library's course reserves, and whether an earlier edition is acceptable (ask; don't assume).
   - Local pickup near campus: Facebook Marketplace and Craigslist listings can be read when public. Never contact a
     seller; show the listing and safety tips.
   - Coupons and price history: look up current promo codes and a price-history page for the item when one exists,
     to say whether today's price is unusually low or high.
   Read each offer's own page to confirm the price, stock, shipping cost and condition. Skip any offer you can't
   confirm on the seller's page.

4. **Compare real totals.** Write the confirmed offers to a file and run, from this Skill's folder:

   ```bash
   python3 scripts/compare.py --offers ~/.config/gapquest/last_offers.json --tax-rate <local sales tax %>
   ```

   The file format is in `references/offers-file.md`. Use the student's local combined sales tax rate (look it up for
   their city once and remember it). The script adds shipping, tax and discounts, ranks by total, and marks the
   cheapest new and cheapest overall. `--sample` runs on a bundled example.

5. **Reply** (see Replies).

6. **If they want to buy.** Ask which offer. Open that page in Cubbie's browser, add the item to the cart and apply
   the coupon, then hand the browser to the student to sign in and pay. Never enter payment details and never place
   the order.

7. **Offer a price watch** if nothing is a good deal yet: "Want me to check again every Monday and text you if it
   drops under $X?" Create the check-in with Cubbie's reminders ability only after a yes, worded to work on its own:
   "GapQuest price watch: search for <exact item> and text the student only if the best total is under
   $<target>, with the link."

## Replies

Short, plain text, no Markdown. Lead with the answer:

"Cheapest new: $189.99 at Best Buy, $202.34 with tax, free pickup on Rural Rd.
Amazon is $199 + tax.
Refurbished on Back Market: $149, 1-year warranty.

Want the link?"

- Always give the total the student will pay, not just the sticker price.
- Say the condition for anything not new, and the return window if it's short.
- Put links on their own line, only for the one or two offers the student is likely to pick.
- If today's price is high compared with its usual price, say so and offer a price watch.
- For marketplace listings, add one short line: meet in a public place on campus, inspect before paying.

## When something fails

- The item is ambiguous: ask one question to pin the model before searching.
- No price can be confirmed: say so and give the retailers to check, rather than guessing a number.
- The script exits with 2 (bad offers file): fix the file and run once more; if it fails again, compare by hand and
  say the totals are approximate.

Never invent a price, a coupon code or a stock status.
