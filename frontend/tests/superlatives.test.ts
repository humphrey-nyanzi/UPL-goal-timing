import assert from "node:assert/strict";
import test from "node:test";

import { formatTeamNames, getExtremeItems } from "../src/utils/superlatives.ts";

test("preserves every team tied for the lowest value", () => {
  const teams = [
    { name: "SC Villa", conceded: 17 },
    { name: "Vipers SC", conceded: 17 },
    { name: "NEC FC", conceded: 20 },
  ];

  const leaders = getExtremeItems(teams, (team) => team.conceded, "asc");

  assert.deepEqual(leaders.map((team) => team.name), ["SC Villa", "Vipers SC"]);
  assert.equal(formatTeamNames(leaders.map((team) => team.name)), "SC Villa and Vipers SC");
});

test("ignores unavailable values when finding an extreme", () => {
  const teams = [
    { name: "Unavailable", conceded: null },
    { name: "Measured", conceded: 19 },
  ];

  assert.deepEqual(getExtremeItems(teams, (team) => team.conceded, "asc"), [teams[1]]);
});
