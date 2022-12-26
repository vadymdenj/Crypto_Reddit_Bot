# Crypto Reddit Bot
## Summary
As someone who is interested in cryptocurrency, I often go on Reddit in search for analysis and discussions related to price of Bitcoin. With high volatility in Bitcoin prices, it’s difficult to understand some of the older discussion and analysis posts as Bitcoin price back then is a big piece of context that is often missing. Instead of Googling “price of Bitcoin on 21st of August 2019”, for example, it would be much more convenient to have the price included somewhere in the thread, so the reader doesn’t have to leave the app to get that information. For this reason, I made a bot that looks for the most upvoted daily post on r/Bitcoin that talks about Bitcoin price action and replies to it with a price of Bitcoin for the day. This allows any reader to have more context when going through popular Bitcoin price threads at any time in the future. 
## Implementation
### Using APIs
To get the required information for the bot, the Python script pulled data from two APIs. Python Reddit API ([PRAW])(https://praw.readthedocs.io/en/stable/) was used to do any Reddit related operations such as signing the bot in, determining the most upvoted post for the day that included price action words from action_words.txt document, and replying to such post. To get the latest price for Bitcoin, [CoinMarketCap] (https://coinmarketcap.com/api/) RESTful API [endpoint] (https://coinmarketcap.com/api/documentation/v1/#operation/getV2CryptocurrencyQuotesLatest) was used to retrieve latest market quote. From there, given a JSON dataset, I used index parsing the get the latest Bitcoin price which was then rounded to the nearest cent and ready to use. 
### Serverless Architecture
After writing the script for a bot, next step was to launch the script somewhere on a preset schedule (once a day) without any actions required on my side. To accomplish this, I turned to AWS. Since the Python script I wrote didn’t require much computing power to execute, I turned to AWS [Lambda] (https://aws.amazon.com/lambda/) since it was serverless, well-integrated with other AWS services and cheap for light workloads. Additionally, running the code on Lambda allows for quick updates and fixes to the code without the need to SSH into any server, which is convenient. The challenge with using Lambda function lied in imported libraries such as praw and requests, which it didn’t recognize in the code. To solve this issue, I installed the needed libraries using pip in a directory on my local machine with the help of AWS Secure Shell. Then, I used zip and saved the package in AWS [S3] (https://aws.amazon.com/s3/) bucket. To make sure Lambda gets the package, I made a Layer which consisted of zip file saved in S3 and attached it to my Lambda function. Next, I needed to make sure my script runs exactly once a day at a specified time. To do that, I used AWS [CloudWatch] (https://aws.amazon.com/cloudwatch/) alarm, which triggered the Lambda function to run daily at the time that I specified, which is 5pm PDT.
### Cost Efficiency
Originally, I tried running the bot on the AWS [EC2] (https://aws.amazon.com/ec2/) On-Demand instance and [EBS] (https://aws.amazon.com/ebs/) volumes attached to them with a wait timer for a day in the code. Despite small EC2 instance size, this configuration of services resulted in around $0.33/day cost of running the bot, which might not seem that much, but it adds up to more than $120/year. Switching to EC2 along with CloudWatch daily alarm would’ve decreased this cost but since EC2 is a virtual server, it requires more work to make changes to code such as SSH into the instance first using key pairs. Therefore, I decided to move away from servers to Lambda paired with CloudWatch and S3. Free 400,000 GB-seconds of computing time per month for Lambda and 10 free alarms for CloudWatch more than cover the capacity at which these services are used to run the bot. This makes the only costs associated with this configuration S3 related. Since the Lambda function requests (GET) zip file in S3 bucket only once a day and S3 pricing is $0.004 per 10,000 GET request per month, the cost rounds to 0, making the bot run free of charge.  