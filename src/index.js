//Import package
// import { Client, auth } from "twitter-api-sdk";
import { getFollowers, getTweets } from "./twt_api.js"
import { sendDyn, scanDyn } from "./dyn_api.js"
import fs from "fs"

const makeFollowersDynObj = (twtObj) => {

    return new Promise((resolve, reject) => {
        const fetchTime = new Date().toISOString().slice(0, -2);
        const twtData = twtObj.data;
        console.log(JSON.stringify(twtObj, null, 2));
        const twtDataPM = twtData.public_metrics;
        if (!twtData.verified) {
            reject("this twitter account is not verified");
        } else {
            resolve(
                {
                    TableName: "twt_api_pjsekai",
                    Item: {
                        fetch_time: { S: fetchTime },
                        followers_count: { N: twtDataPM.followers_count.toString() }
                    }
                }
            );
        }
    })
};

const scanParam = { TableName: "twt_api_1min" };
const userName = "pj_sekai"

const flwObj = await getFollowers(userName);
/* DEPRECATED to be deleted*/
// const dynObj = await makeFollowersDynObj(flwObj)
// sendDyn(dynObj);
/* DEPRECATED to be deleted*/

console.log("User id: " + flwObj.data.id);
const twtArr = await getTweets(flwObj.data.id);
console.log(JSON.stringify(twtArr.slice(-2, -1), null, 2));
console.log("Tweet data size: " + twtArr.length);

for (const twt of twtArr) {
    console.log(`${twt.created_at} https://twitter.com/${userName}/status/${twt.id}`)
};


// const dynScan = await scanDyn(scanParam);
// if (dynScan["$metadata"].httpStatusCode == "200") {
//     console.log("data succcessfully scanned. count: " + dynScan["Count"]);
// } else {
//     console.log("ERROR at scan");
//     console.log(JSON.stringify(dynScan, null, 2));
// }
// const outputCsv = dynScan.Items.reduce((prev, curr) => {
//     prev += `"${curr["fetch_time"]["S"]}","${curr["followers_count"]["N"]}"\n`;
//     return prev;
// }, '"fetch_time","followers_count"\n');
// fs.writeFileSync("./results.csv", outputCsv);