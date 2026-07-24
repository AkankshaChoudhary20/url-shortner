interface ExpiryBadgeProps {
  expiresAt: string | null;
  isExpired: boolean;
}

export function ExpiryBadge({ expiresAt, isExpired }: ExpiryBadgeProps) {
  if (expiresAt === null) {
    return <span className="badge badge-neutral">Never expires</span>;
  }

  return isExpired ? (
    <span className="badge badge-danger">Expired</span>
  ) : (
    <span className="badge badge-info">Expires {new Date(expiresAt).toLocaleString()}</span>
  );
}
