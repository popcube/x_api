import * as AWS from "@aws-sdk/client-dynamodb";
import { setTimeout } from 'node:timers/promises';

const client = new AWS.DynamoDB({
    credentials: {
        accessKeyId: process.env.ACC_KEY,
        secretAccessKey: process.env.SEC_ACC_KEY
    },
    region: "ap-northeast-1"
});

export const sendDyn = (dynObj) => {
    client.putItem(dynObj, function (err, data) {
        if (err) console.log(err);
        else console.log("Data successfully sent at " + dynObj.Item.fetch_time.S)
    });
}

export const scanDyn = async (dynObj) => {
    const returnData = [];
    while (true) {
        const scannedData = await client.scan(dynObj);
        if (scannedData["$metadata"].httpStatusCode == "200") {
            returnData.push(...scannedData.Items);
            if (!scannedData["LastEvaluatedKey"]) {
                console.log("data succcessfully scanned. count: " + scannedData["Count"] + ", done!");
                break;
            }
            else {
                console.log("data succcessfully scanned. count: " + scannedData["Count"] + ", paginating...");
            }
        } else {
            console.log("ERROR at scan");
            console.log(JSON.stringify(scannedData, null, 2));
            throw new Error('ERROR at scan');
        }
        dynObj["ExclusiveStartKey"] = scannedData["LastEvaluatedKey"]
        await setTimeout(1000);
    }
    return returnData;
}

export const queryDyn = async (dynObj) => {
    const returnData = [];
    while (true) {
        const scannedData = await client.query(dynObj);
        if (scannedData["$metadata"].httpStatusCode == "200") {
            returnData.push(...scannedData.Items);
            if (!scannedData["LastEvaluatedKey"]) {
                console.log("data succcessfully queried. count: " + scannedData["Count"] + ", done!");
                break;
            }
            else {
                console.log("data succcessfully queried. count: " + scannedData["Count"] + ", paginating...");
            }
        } else {
            console.log("ERROR at query");
            console.log(JSON.stringify(scannedData, null, 2));
            throw new Error('ERROR at query');
        }
        dynObj["ExclusiveStartKey"] = scannedData["LastEvaluatedKey"]
        await setTimeout(1000);
    }
    return returnData;
}