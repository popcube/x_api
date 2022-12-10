import * as AWS from "@aws-sdk/client-dynamodb";
const client = new AWS.DynamoDB({
    accessKeyId: process.env.ACC_KEY,
    secretAccessKey: process.env.SEC_ACC_KEY,
    region: "REGION"
});

const documentClient = client.DocumentClient();

const params = {
    TableName: 'twt_api_pjsekai',
    Key: {
        "fetch_time": "2022-12-07T17:52:00"
    }
}
documentClient.get(params, (err, data) => {
    if (err) console.log(JSON.stringify(err, null, 2))
    else console.log(JSON.stringify(data, null, 2))
})

// // async/await.
// try {
//     const data = await client.batchExecuteStatement(params);
//     // process data.
// } catch (error) {
//     // error handling.
// }

// // Promises.
// client
//     .batchExecuteStatement(params)
//     .then((data) => {
//         // process data.
//     })
//     .catch((error) => {
//         // error handling.
//     });

// // callbacks.
// client.batchExecuteStatement(params, (err, data) => {
//     // process err and data.
// });