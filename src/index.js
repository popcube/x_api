//Import package
// import { Client, auth } from "twitter-api-sdk";
import { getFollowers, getTweets } from "./get_data.js"
import { sendDyn } from "./send_data.js"

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




const flwObj = await getFollowers();
// const dynObj = await makeFollowersDynObj(flwObj)
// sendDyn(dynObj);

console.log(flwObj.data.id);
const twtArr = await getTweets(flwObj.data.id);
console.log(JSON.stringify(twtArr, null, 2));
console.log(twtArr.length);