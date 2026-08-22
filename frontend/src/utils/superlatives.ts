export type ExtremeDirection = "asc" | "desc";

export function getExtremeItems<T>(
  items: T[],
  getValue: (item: T) => number | null,
  direction: ExtremeDirection = "desc",
) {
  const measuredItems = items
    .map((item) => ({ item, value: getValue(item) }))
    .filter((entry): entry is { item: T; value: number } => entry.value !== null);

  if (measuredItems.length === 0) return [];

  const values = measuredItems.map((entry) => entry.value);
  const extremeValue = direction === "desc" ? Math.max(...values) : Math.min(...values);
  return measuredItems.filter((entry) => entry.value === extremeValue).map((entry) => entry.item);
}

export function formatTeamNames(teamNames: string[]) {
  if (teamNames.length <= 1) return teamNames[0] ?? "";
  if (teamNames.length === 2) return teamNames.join(" and ");
  return `${teamNames.slice(0, -1).join(", ")}, and ${teamNames.at(-1)}`;
}
