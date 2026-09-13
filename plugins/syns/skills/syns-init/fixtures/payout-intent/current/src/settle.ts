export function recipient(tx: Transaction): Address {
  return tx.sponsor ? tx.recipientOverride ?? tx.sponsor : tx.recipient;
}
