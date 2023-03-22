import { queryDyn } from "./dyn_api.js"
import fs from "fs"

// DO NOT DELETE BELOW

queryParam = { TableName: "twt_main_flwers", account: "pj_sekai" };

const dynQuery = await queryDyn(queryParam);

const outputCsv = dynQuery.reduce((prev, curr) => {
  prev += `${curr["fetch_time"]["S"]},${curr["followers_count"]["N"]}\n`;
  return prev;
}, 'fetch_time,followers_count\n');
fs.writeFileSync("./results.csv", outputCsv);