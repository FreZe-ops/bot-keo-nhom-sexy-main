const fs = require("fs");
const axios = require("axios");

async function main() {
  for (const ns of [1, 2]) {
    const log = fs.readFileSync(`/root/.pm2/logs/session-sexy-${ns}-out.log`, "utf8");
    const matches = [
      ...log.matchAll(
        /(https:\/\/[^/\s]+)\/player\/query\/[^;\s]+;jsessionid=([A-Za-z0-9]+)/g
      ),
    ];
    const last = matches.at(-1);
    if (!last) {
      console.log(`NS${ns}: no current hall URL/session`);
      continue;
    }
    const [, origin, sessionId] = last;
    const cookieMatches = [...log.matchAll(/\[COOKIE\] Full cookie: (.+)/g)];
    const cookie = cookieMatches.at(-1)?.[1]?.trim() || "";
    console.log(`NS${ns}: ${origin} session=${sessionId.slice(0, 8)}...`);
    for (const endpoint of [
      "queryInitWebGameHall",
      "queryWebGameHallInformation",
      "queryWebGameHallRoad",
    ]) {
      const url = `${origin}/player/query/${endpoint};jsessionid=${sessionId}`;
      try {
        const body = new URLSearchParams({ gameGroupId: "2" });
        const res = await axios.post(url, body, {
          timeout: 20000,
          headers: {
            accept: "application/json, text/plain, */*",
            "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
            cookie,
          },
        });
        const data = res.data;
        console.log(
          `  ${endpoint}: status=${res.status} keys=${
            data && typeof data === "object" ? Object.keys(data).join(",") : typeof data
          } tableItems=${Array.isArray(data?.tableItems) ? data.tableItems.length : "-"} ` +
          `sample=${typeof data === "string" ? JSON.stringify(data.slice(0, 180)) : "-"}`
        );
      } catch (e) {
        console.log(`  ${endpoint}: ERROR ${e.response?.status || ""} ${e.message}`);
      }
    }
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
