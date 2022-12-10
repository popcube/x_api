import * as AWS from "@aws-sdk/client-dynamodb";
const documentClient = new AWS.DynamoDB({
    credentials: {
        accessKeyId: process.env.ACC_KEY,
        secretAccessKey: process.env.SEC_ACC_KEY
    },
    region: "ap-northeast-1"
});

// const documentClient = new client.DocumentClient();

const params = [
    {
        "statements": "SELECT * from twt_api_pjsekai"
    }
]

const main = () => {
    documentClient.batchExecuteStatement(params, (err, data) => {
        if (err) console.log(JSON.stringify(err, null, 2))
        else console.log(JSON.stringify(data, null, 2))
    });
}

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

export default main;