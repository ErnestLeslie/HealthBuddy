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
using System.Drawing;

namespace HealthBuddyWebApp
{
    public partial class Emergency : System.Web.UI.Page
    {
        private static AmazonDynamoDBClient client = new AmazonDynamoDBClient();
        DataTable dt = new DataTable();
        protected void Page_Load(object sender, EventArgs e)
        {
            Session["PageName"] = "Emergency";
            if (!IsPostBack)
            {
                dt = ScanRequest();
                dt.DefaultView.Sort = "Ward Number ASC";
                gv_Emergency.DataSource = dt;
                gv_Emergency.DataBind();
            }
        }

        public DataTable ScanRequest()
        {
            var request = new ScanRequest
            {
                TableName = "Emergencies",
                ProjectionExpression = "bedNo, wardNo"
            };

            var response = client.Scan(request);
            DataTable dt = new DataTable();
            dt.Columns.Add(new DataColumn("Ward Number"));
            dt.Columns.Add(new DataColumn("Bed Number"));

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
                        idx++;
                    }
                    if (attributeName.Equals("wardNo"))
                    {
                        attributeName = "Ward Number";
                        newPatientRow[attributeName] = value.S;
                        idx++;
                    }
                }
                dt.Rows.Add(newPatientRow);
            }
            return dt;
        }

        protected void gv_Emergency_RowDeleting(object sender, GridViewDeleteEventArgs e)
        {
            GridViewRow row = gv_Emergency.Rows[e.RowIndex];
            int id = Convert.ToInt32(row.Cells[1].Text);
            string PatientID = id.ToString();
            string bednoumber = row.Cells[2].Text;

            string deviceID = get_device_ID(PatientID, bednoumber);
            if (!deviceID.Equals("0"))
            {
                //Delete
                delete_patient(deviceID);

                //Bind the New Results 
                dt = ScanRequest();
                Session["DataTable"] = dt;

                //Reset the edit index.
                gv_Emergency.EditIndex = -1;

                //Bind data to the GridView control.
                dt = ScanRequest();
                dt.DefaultView.Sort = "Ward Number ASC";
                gv_Emergency.DataSource = dt;
                gv_Emergency.DataBind();
            }
            else
            {
                Label1.Text = "ERROR";
            }
        }
            
        protected void delete_patient(string patientID)
        {
            string tableName = "Emergencies";

            var request = new DeleteItemRequest
            {
                TableName = tableName,
                Key = new Dictionary<string, AttributeValue>() {
                    { "deviceID", new AttributeValue { S = patientID } } },
            };

            var response = client.DeleteItem(request);
        }

        protected string get_device_ID(string ward,string bed)
        {
            var request = new ScanRequest
            {
                TableName = "Emergencies",
                ProjectionExpression = "deviceID",
                FilterExpression="wardNo = :ward and bedNo = :bed",
                ExpressionAttributeValues = new Dictionary<string, AttributeValue> {
                                {":ward", new AttributeValue { S = ward }},
                                {":bed", new AttributeValue { S = bed }}
                }
            };
            var response = client.Scan(request);
            int count = response.Items.Count;
            if (count > 0)
            {
                foreach (Dictionary<string, AttributeValue> keyValuePair in response.Items)
                {
                    foreach (KeyValuePair<string, AttributeValue> kvp in keyValuePair)
                    {
                        string attributeName = kvp.Key;
                        AttributeValue value = kvp.Value;
                        return value.S;
                    }
                }
            }
            return "0";
        }
    }
}