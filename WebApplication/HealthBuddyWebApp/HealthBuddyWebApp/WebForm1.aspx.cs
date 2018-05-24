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
    public partial class WebForm1 : System.Web.UI.Page
    {
        DataTable dt = new DataTable();

        private static AmazonDynamoDBClient client = new AmazonDynamoDBClient();
        protected void Page_Load(object sender, EventArgs e)
        {
            if (!IsPostBack)
            {
                DataTable dt = ScanRequest();
                Session["Sort"] = "Patient ID ASC";
                dt.DefaultView.Sort = "Patient ID ASC";
                BindGridView(dt);
                Session["DataTable"] = dt;
            }
        }

        public void BindGridView(DataTable dt)
        {
            GridView1.DataSource = dt;
            GridView1.DataBind();
        }
        public DataTable ScanRequest()
        {
            var request = new ScanRequest
            {
                TableName = "Patients",
                ProjectionExpression = "RoundingID, patientname, phoneNumber, DeviceID"
            };

            var response = client.Scan(request);
            dt.Columns.Add(new DataColumn("Patient ID"));
            dt.Columns.Add(new DataColumn("Patient Name"));
            dt.Columns.Add(new DataColumn("Phone Number"));

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
                    if (attributeName.Equals("phoneNumber"))
                    {
                        attributeName = "Phone Number";
                        newPatientRow[attributeName] = value.S;
                        idx++;
                    }
                    if (attributeName.Equals("patientname"))
                    {
                        attributeName = "Patient Name";
                        newPatientRow[attributeName] = value.S;
                        idx++;
                    }
                    if (attributeName.Equals("RoundingID"))
                    {
                        attributeName = "Patient ID";
                        newPatientRow[attributeName] = value.N;
                        idx++;
                    }
                    if (attributeName.Equals("DeviceID"))
                    {
                        string deviceID = value.S;
                        var request2 = new ScanRequest
                        {
                            TableName = "Devices",
                            ProjectionExpression = "bedNo, wardNo",
                            FilterExpression = "deviceID = :val",
                            ExpressionAttributeValues = new Dictionary<string, AttributeValue> {
                                {":val", new AttributeValue { S = deviceID }}
                            }
                        };
                        var response2 = client.Scan(request2);
                        foreach (Dictionary<string, AttributeValue> deviceKeyValuePair in response2.Items)
                        {
                            foreach (KeyValuePair<string, AttributeValue> kvp2 in deviceKeyValuePair)
                            {
                                string attributeName2 = kvp2.Key;
                                AttributeValue value2 = kvp2.Value;
                                if (attributeName2.Equals("bedNo"))
                                {
                                    attributeName = "Ward Number";
                                    newPatientRow[attributeName] = value2.S;
                                    idx++;
                                }
                                if (attributeName2.Equals("wardNo"))
                                {
                                    attributeName = "Bed Number";
                                    newPatientRow[attributeName] = value2.S;
                                    idx++;
                                }
                            }
                        }
                    }
                    //Label1.Text += attributeName + ": " + "<br>" +
                    //    (value.S == null ? "" : value.S) + "" +
                    //    (value.N == null ? "" : value.N) + "<br>";
                }
                dt.Rows.Add(newPatientRow);
                //Label1.Text += "************************************************<br>";
            }
            return dt;
        }

        protected void DropDownList1_SelectedIndexChanged(object sender, EventArgs e)
        {
            string sortBy = DropDownList1.SelectedValue;
            Session["Sort"] = sortBy;
            DataTable dt = (DataTable)Session["DataTable"];
            dt.DefaultView.Sort = sortBy;
            GridView1.DataSource = dt;
            GridView1.DataBind();
        }

        public void updateItem(string patientID, Dictionary<string, AttributeValue> ExpressionAttributeValues )
        {
            var request = new UpdateItemRequest
            {
                TableName = "Patients",
                Key = new Dictionary<string, AttributeValue>() { { "RoundingID", new AttributeValue { N = patientID } } },
                ExpressionAttributeNames = new Dictionary<string, string>()
                {
                    {"#N", "patientname"},
                    {"#P", "phoneNumber"}
                },
                ExpressionAttributeValues = ExpressionAttributeValues,
                    // This expression does the following:
                    // 1) Change Name
                    // 2) Change Phone
                    UpdateExpression = "SET #N = :name, #P = :phone"
                };
                var response = client.UpdateItem(request);
        }

        protected void GridView1_SelectedIndexChanged(object sender, EventArgs e)
        {
            string value = GridView1.SelectedRow.Cells[3].Text;
            label1.Text = value;
        }

        protected void GridView1_RowEditing(object sender, GridViewEditEventArgs e)
        {
            //Set the edit index.
            GridView1.EditIndex = e.NewEditIndex;
            DataTable dt = (DataTable)Session["DataTable"];
            //Bind data to the GridView control.
            BindGridView(dt);
        }

        protected void GridView1_RowUpdating(object sender, GridViewUpdateEventArgs e)
        {
            DataTable dt = (DataTable)Session["DataTable"];
            //Get the Patient ID
            GridViewRow row = GridView1.Rows[e.RowIndex];
            int id = Convert.ToInt32(row.Cells[1].Text);
            string PatientID = id.ToString();
            //Basically,
            //Patient Name = ((TextBox)(row.Cells[2].Controls[0])).Text;
            //Phone Number = ((TextBox)(row.Cells[3].Controls[0])).Text;
            //Ward No = ((TextBox)(row.Cells[4].Controls[0])).Text;
            //Bed No = ((TextBox)(row.Cells[5].Controls[0])).Text;

            string PatientName = ((TextBox)(row.Cells[2].Controls[0])).Text;
            string PatientPhone = ((TextBox)(row.Cells[3].Controls[0])).Text;
            string WardNo = ((TextBox)(row.Cells[4].Controls[0])).Text;
            string BedNo = ((TextBox)(row.Cells[5].Controls[0])).Text;

            //Create the Dictionary to Pass on to the update method
            Dictionary<string, AttributeValue> expressionpatient = new Dictionary<string, AttributeValue>()
                {
                    {":name",new AttributeValue { S = PatientName }},
                    {":phone",new AttributeValue { S = PatientPhone }},
                };

            //Call the Update Method
            updateItem(PatientID, expressionpatient);

            //Bind the New Results 
            dt = ScanRequest();
            Session["DataTable"] = dt;
            dt.DefaultView.Sort = Session["Sort"].ToString();

            //Reset the edit index.
            GridView1.EditIndex = -1;

            //Bind data to the GridView control.
            BindGridView(dt);
        }

        protected void GridView1_RowCancelingEdit(object sender, GridViewCancelEditEventArgs e)
        {
            //Reset the edit index.
            GridView1.EditIndex = -1;
            DataTable dt = (DataTable)Session["DataTable"];
            //Bind data to the GridView control.
            BindGridView(dt);
        }
    }   
}