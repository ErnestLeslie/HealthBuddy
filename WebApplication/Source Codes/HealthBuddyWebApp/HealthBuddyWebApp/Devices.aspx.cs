using System;
using System.Drawing.Printing;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.UI;
using Amazon.DynamoDBv2;
using Amazon.DynamoDBv2.Model;
using Amazon.Runtime;
using System.Data;
using System.Web.UI.WebControls;
namespace HealthBuddyWebApp
{
    public partial class Devices : System.Web.UI.Page
    {
        DataTable dt = new DataTable();
        private static AmazonDynamoDBClient client = new AmazonDynamoDBClient();

        protected void Page_Load(object sender, EventArgs e)
        {
            Session["PageName"] = "Devices";
            if (!IsPostBack)
            {
                DataTable dt2 = bindDevices();
                Session["DataTable"] = dt2;
                dt2.DefaultView.Sort = "Ward Number ASC";
                gv_Devices.DataSource = dt2;
                gv_Devices.DataBind();
            }
        }
        protected DataTable bindDevices()
        {
            var request = new ScanRequest
            {
                TableName = "Devices",
                ProjectionExpression = "deviceID,bedNo,wardNo"
            };
            var response = client.Scan(request);
            dt.Columns.Add(new DataColumn("Ward Number"));
            dt.Columns.Add(new DataColumn("Bed Number"));
            dt.Columns.Add(new DataColumn("Device ID"));
            foreach (Dictionary<string, AttributeValue> keyValuePair in response.Items)
            {
                DataRow newPatientRow = dt.NewRow();
                int idx = 0;
                foreach (KeyValuePair<string, AttributeValue> kvp in keyValuePair)
                {
                    string attributeName = kvp.Key;
                    AttributeValue value = kvp.Value;
                    if (attributeName.Equals("bedNo"))
                    {
                        attributeName = "Bed Number";
                        newPatientRow[attributeName] = value.S;
                    }
                    if (attributeName.Equals("wardNo"))
                    {
                        attributeName = "Ward Number";
                        newPatientRow[attributeName] = value.S;
                    }
                    if (attributeName.Equals("deviceID"))
                    {
                        attributeName = "Device ID";
                        newPatientRow[attributeName] = "AMZN1.ASK.DEVICE..." + value.S.Substring(value.S.Length - 5);
                    }
                }
                dt.Rows.Add(newPatientRow);
            }
            return dt;
        }
        public void BindGridView(DataTable dt)
        {
            gv_Devices.DataSource = dt;
            gv_Devices.DataBind();
        }
        protected void delete_patient(string deviceID)
        {
            string tableName = "Devices";

            var request = new DeleteItemRequest
            {
                TableName = tableName,
                Key = new Dictionary<string, AttributeValue>() {
                    { "deviceID", new AttributeValue { S = deviceID } } },
            };

            var response = client.DeleteItem(request);
        }
    }
}