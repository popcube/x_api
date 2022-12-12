//Import package
// import { Client, auth } from "twitter-api-sdk";
import get_data from "./get_data.js"
import send_data from "./send_data.js"

const makeDynObj = (twtObj) => {

    return new Promise((resolve, reject) => {
        const fetchTime = new Date().toISOString().slice(0, -2);
        const twtData = twtObj.data;
        // console.log(JSON.stringify(twtObj, null, 2));
        const twtDataPM = twtData.public_metrics;
        if (twtData.verified) {
            reject("this twitter account is not verified");
        } else {
            resolve(
            {
                TableName: "twt_api_pjsekai",
                Item: {
                    fetch_time: { S: fetchTime },
                    followers_count: { N: twtDataPM.followers_count.toString() },
                    following_count: { N: twtDataPM.following_count.toString() },
                    listed_count: { N: twtDataPM.listed_count.toString() },
                    tweet_count: { N: twtDataPM.tweet_count.toString() }
                    },
                    // data: {
                    //     M: {
                    //         username: { S: twtData.username },
                    //         id: { S: twtData.id },
                    //         name: { S: twtData.name },
                    //         public_metrics: {
                    //             M: {
                    //                 followers_count: { N: twtDataPM.followers_count.toString() },
                    //                 following_count: { N: twtDataPM.following_count.toString() },
                    //                 listed_count: { N: twtDataPM.listed_count.toString() },
                    //                 tweet_count: { N: twtDataPM.tweet_count.toString() }
                    //             }
                    //         },
                    //         verified: { BOOL: twtData.verified }
                    //     }
                    // }
                }
            }
        );
        }
    })
};




const twtObj = await get_data();
const dynObj = await makeDynObj(twtObj)
// console.log(JSON.stringify(dynObj, null, 2));
send_data(dynObj);