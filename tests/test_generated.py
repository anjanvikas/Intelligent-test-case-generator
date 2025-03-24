java
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.By;
import org.openqa.selenium.WebElement;
import org.junit.Assert;

import java.util.Arrays;
import java.util.Collection;

@RunWith(Parameterized.class)
public class WebAppTest {

    private String username;
    private String password;
    private String expectedOutcome;
    private WebDriver driver;

    public WebAppTest(String username, String password, String expectedOutcome) {
        this.username = username;
        this.password = password;
        this.expectedOutcome = expectedOutcome;
    }

    @Parameterized.Parameters
    public static Collection<Object[]> testData() {
        return Arrays.asList(new Object[][]{
                {"testUser", "testPassword", "User is logged in"},
                {"invalidUser", "testPassword", "Error message is displayed"},
                {"testUser", "invalidPassword", "Error message is displayed"},
                {"testUser!@#", "testPassword!@#", "User is logged in"},
                {" testUser ", " testPassword ", "User is logged in"},
                {"noAccountUser", "noAccountPassword", "Message indicating no accounts is displayed"}
        });
    }

    @Before
    public void setUp() {
        System.setProperty("webdriver.chrome.driver", "path/to/chromedriver");
        driver = new ChromeDriver();
        driver.get("Application URL");
    }

    @Test
    public void testLogin() {
        WebElement usernameField = driver.findElement(By.name("username"));
        WebElement passwordField = driver.findElement(By.name("password"));

        usernameField.sendKeys(username);
        passwordField.sendKeys(password);

        WebElement loginButton = driver.findElement(By.name("login"));
        loginButton.click();

        String actualOutcome;
        if (driver.getCurrentUrl().contains("Account overview endpoint")) {
            actualOutcome = "User is logged in";
        } else if (driver.getPageSource().contains("Error message")) {
            actualOutcome = "Error message is displayed";
        } else if (driver.getPageSource().contains("Message indicating no accounts")) {
            actualOutcome = "Message indicating no accounts is displayed";
        } else {
            actualOutcome = "Failure";
        }

        Assert.assertEquals(expectedOutcome, actualOutcome);
    }

    @After
    public void tearDown() {
        driver.quit();
    }
}