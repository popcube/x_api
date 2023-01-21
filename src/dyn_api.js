import * as AWS from "@aws-sdk/client-dynamodb";
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
    var returnData = [];
    while (true) {
        const scannedData = await client.scan(dynObj);
        if (scannedData["$metadata"].httpStatusCode == "200") {
            returnData = returnData.concat(scannedData.Items);
            if (!Object.keys(scannedData["LastEvaluatedKey"]).length) {
                console.log("data succcessfully scanned. count: " + scannedData["Count"] + ", done!");
            }
            else {
                console.log("data succcessfully scanned. count: " + scannedData["Count"] + ", pagenating...");
                break;
            }
        } else {
            console.log("ERROR at scan");
            console.log(JSON.stringify(dynScan, null, 2));
            throw new Error('ERROR at scan');
        }
        dynObj["ExclusiveStartKey"] = scannedData["LastEvaluatedKey"]

    }
    return scannedData;
}