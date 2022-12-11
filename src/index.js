//Import package
// import { Client, auth } from "twitter-api-sdk";
import get_data from "./get_data.js"
import send_data from "./send_data.js"

const makeDynObj = (twtObj) => {
    const fetchTime = new Date().toISOString().slice(0, -2);

    return {
        TableName: "twt_api_pjsekai",
        Item: {
            fetch_time: { S: fetchTime }
        }
    };
}




const twtObj = get_data();
// send_data();