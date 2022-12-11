//Import package
// import { Client, auth } from "twitter-api-sdk";
import get_data from "./get_data.js"
import send_data from "./send_data.js"

const makeDynObj = (twtObj) => {

    return new Promise((resolve) => {
        const fetchTime = new Date().toISOString().slice(0, -2);
        resolve(
            {
                TableName: "twt_api_pjsekai",
                Item: {
                    fetch_time: { S: fetchTime }
                }
            }
        )
    });
}




const twtObj = get_data();
const dynObj = await makeDynObj(twtObj)
send_data(dynObj);