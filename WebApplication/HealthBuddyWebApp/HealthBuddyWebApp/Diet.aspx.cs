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
using Amazon.SimpleNotificationService.Model;
using Amazon.SimpleNotificationService;

namespace HealthBuddyWebApp
{
    public partial class Diet : System.Web.UI.Page
    {
        DataTable dt = new DataTable();
        private static AmazonDynamoDBClient client = new AmazonDynamoDBClient();

        protected void Page_Load(object sender, EventArgs e)
        {
            if (!IsPostBack)
            {
                DataTable dt = bind_LIST();
                Session["DataTable"] = dt;
                lv_Address.DataSource = dt;
                lv_Address.DataBind();
                lbl_roundingCount.Text = get_Count("Western").ToString();
                lbl_ActiveRoundingCount.Text = get_Count("Chinese").ToString();
                lbl_OutdatedRoundingCount.Text = get_Count("Muslim").ToString();
                lbl_LastestRounding.Text  = get_Count("Vegetarian").ToString();
				lbl_unselected.Text = get_Not_Chosen_Count().ToString();
            }
            Session["PageName"] = "Diets";
            
        }

        protected DataTable bind_LIST()
        {
            var request = new ScanRequest
            {
                TableName = "Diets",
                ProjectionExpression = "Chinese,Muslim,Vegetarian,Western",
            };

            var response = client.Scan(request);
            dt.Columns.Add(new DataColumn("Western"));
            dt.Columns.Add(new DataColumn("Chinese"));
            dt.Columns.Add(new DataColumn("Muslim"));
            dt.Columns.Add(new DataColumn("Vegetarian"));
            foreach (Dictionary<string, AttributeValue> keyValuePair in response.Items)
            {
                DataRow newPatientRow = dt.NewRow();
                foreach (KeyValuePair<string, AttributeValue> kvp in keyValuePair)
                {
                    string attributeName = kvp.Key;
                    AttributeValue value = kvp.Value;
                    if (attributeName.Equals("Western"))
                    {
                        attributeName = "Western";
                        newPatientRow[attributeName] = value.S;
                    }
                    if (attributeName.Equals("Chinese"))
                    {
                        attributeName = "Chinese";
                        newPatientRow[attributeName] = value.S;
                    }
                    if (attributeName.Equals("Muslim"))
                    {
                        attributeName = "Muslim";
                        newPatientRow[attributeName] = value.S;
                    }
                    if (attributeName.Equals("Vegetarian"))
                    {
                        attributeName = "Vegetarian";
                        newPatientRow[attributeName] = value.S;
                    }
                }
                dt.Rows.Add(newPatientRow);
            }
            return dt;
        }

        protected void lv_Address_ItemEditing(object sender, ListViewEditEventArgs e)
        {
            lv_Address.EditIndex = e.NewEditIndex;
            DataTable dt = (DataTable)Session["DataTable"];
            lv_Address.DataSource = dt;
            lv_Address.DataBind();
        }

        protected void lv_Address_ItemCanceling(object sender, ListViewCancelEventArgs e)
        {
            lv_Address.EditIndex = -1;
            DataTable dt = (DataTable)Session["DataTable"];
            lv_Address.DataSource = dt;
            lv_Address.DataBind();
        }
		protected int get_Not_Chosen_Count(){
			int western = Convert.ToInt32(lbl_roundingCount.Text);
			int chinese = Convert.ToInt32(lbl_ActiveRoundingCount.Text);
			int muslim = Convert.ToInt32(lbl_OutdatedRoundingCount.Text);
			int vegetarian = Convert.ToInt32(lbl_LastestRounding.Text);
			
			int total = western + chinese + muslim + vegetarian;

			var request = new ScanRequest
            {
                TableName = "Patients",
                FilterExpression = "inUse = :inUse",
                ExpressionAttributeValues = new Dictionary<string, AttributeValue> {
                                {":inUse", new AttributeValue { N = "1" }}
                }
            };

            var response = client.Scan(request);
            int count = response.Items.Count;
            return count - total;
		}
        protected int get_Count(string cuisine)
        {
            var request = new ScanRequest
            {
                TableName = "Patients",
                FilterExpression = "attribute_exists(Diet) and Diet = :inUse and inUse = :usage",
                ExpressionAttributeValues = new Dictionary<string, AttributeValue> {
                                {":inUse", new AttributeValue { S = cuisine }},
                                {":usage", new AttributeValue { N = "1" }}
                }
            };

            var response = client.Scan(request);
            int count = response.Items.Count;
            if (count > 0)
            {
                return count;
            }
            else if (count == 0)
            {
                return 0;
            }
            return 0;
        }

        protected void lv_Address_ItemUpdating(object sender, ListViewUpdateEventArgs e)
        {
          
            string western = "", chinese = "", muslim = "", veg = "";
            TextBox txt = (lv_Address.Items[e.ItemIndex].FindControl("tb_Western")) as TextBox;
            if (txt.Text.Length > 0)
            {
                western = txt.Text;
            }
            txt = (lv_Address.Items[e.ItemIndex].FindControl("tb_Chinese")) as TextBox;
            if (txt.Text.Length > 0)
            {
                chinese = txt.Text;

            }
            txt = (lv_Address.Items[e.ItemIndex].FindControl("tb_Muslim")) as TextBox;
            if (txt.Text.Length > 0)
            {
                muslim = txt.Text;

            }
            txt = (lv_Address.Items[e.ItemIndex].FindControl("tb_Veg")) as TextBox;
            if (txt.Text.Length > 0)
            {
                veg = txt.Text;
            }

            if (veg.Length == 0 || muslim.Length == 0 || chinese.Length == 0 || western.Length == 0)
            {
                Label lbl = (lv_Address.Items[e.ItemIndex].FindControl("lbl_Error")) as Label;
                lbl.Text = "Please ensure all fields are filled.";
            }
            else if (veg.Length > 0 && muslim.Length > 0 && chinese.Length > 0 && western.Length > 0)
            {
                string zero = "0";
                Dictionary<string, AttributeValue> expressionpatient = new Dictionary<string, AttributeValue>()
                    {
                        {":name",new AttributeValue { S = western }},
                        {":phone",new AttributeValue { S = chinese }},
                        {":deviceID",new AttributeValue { S = muslim }},
                        {":inUse",new AttributeValue { S = veg }}
                    };
                var request = new UpdateItemRequest
                {
                    TableName = "Diets",
                    Key = new Dictionary<string, AttributeValue>() { { "dietOption", new AttributeValue { S = zero } } },
                    ExpressionAttributeNames = new Dictionary<string, string>()
                {
                    {"#N", "Western"},
                    {"#P", "Chinese"},
                    {"#D", "Muslim" },
                    {"#U", "Vegetarian"  }
                },
                    ExpressionAttributeValues = expressionpatient,
                    UpdateExpression = "SET #N = :name, #P = :phone, #D = :deviceID, #U = :inUse"
                };
                var response = client.UpdateItem(request);

                Label lbl = (lv_Address.Items[e.ItemIndex].FindControl("lbl_Error")) as Label;
                lbl_12334.ForeColor = Color.DarkGreen;
                lbl_12334.Text = "Success";
                lv_Address.EditIndex = -1;
                DataTable dt = new DataTable();
                dt = bind_LIST();
                Session["DataTable"] = dt;
                lv_Address.DataSource = dt;
                lv_Address.DataBind();
            }
        }
    }
}