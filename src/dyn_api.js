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

export const scanDyn = async () => {
    await client.Scan(dynObj, function (err, data) {
        if (err) console.log(err);
        else console.log("Data successfully scanned at " + dynObj.Item.fetch_time.S)
    });
}