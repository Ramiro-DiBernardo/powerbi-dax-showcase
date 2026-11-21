# DAX measures

All 25 measures live in the `_Measures` table, grouped in display folders. Every measure was validated with DAX queries against the data (see README).

## 1. Base

### Sales Amount

```dax
SUMX(Sales, Sales[Quantity] * Sales[UnitPrice] * (1 - Sales[DiscountPct]))
```

### Total Cost

```dax
SUMX(Sales, Sales[Quantity] * Sales[UnitCost])
```

### Gross Margin

```dax
[Sales Amount] - [Total Cost]
```

### Gross Margin %

```dax
DIVIDE([Gross Margin], [Sales Amount])
```

### Orders

```dax
DISTINCTCOUNT(Sales[OrderID])
```

### Units Sold

```dax
SUM(Sales[Quantity])
```

### Avg Order Value

```dax
DIVIDE([Sales Amount], [Orders])
```

### Discount Amount

```dax
SUMX(Sales, Sales[Quantity] * Sales[UnitPrice] * Sales[DiscountPct])
```

### Online Sales %

```dax
DIVIDE(CALCULATE([Sales Amount], Stores[Channel] = "Online"), [Sales Amount])
```

### Weekend Sales %

```dax
DIVIDE(CALCULATE([Sales Amount], 'Date'[Is Weekend] = TRUE()), [Sales Amount])
```

## 2. Time intelligence

### Sales YTD

```dax
TOTALYTD([Sales Amount], 'Date'[Date])
```

### Sales PY

```dax
CALCULATE([Sales Amount], SAMEPERIODLASTYEAR('Date'[Date]))
```

### Sales YoY %

```dax
VAR _LastYear = MAX('Date'[Year])
VAR _cy = CALCULATE([Sales Amount], 'Date'[Year] = _LastYear)
VAR _py = CALCULATE([Sales PY], 'Date'[Year] = _LastYear)
RETURN IF(NOT ISBLANK(_py), DIVIDE(_cy - _py, _py))
```

### Sales MTD

```dax
TOTALMTD([Sales Amount], 'Date'[Date])
```

### Sales Rolling 3M

```dax
CALCULATE([Sales Amount], DATESINPERIOD('Date'[Date], MAX('Date'[Date]), -3, MONTH))
```

## 3. Share & ranking

### % of Total Sales

```dax
DIVIDE([Sales Amount], CALCULATE([Sales Amount], ALL(Products)))
```

### % of Category

```dax
DIVIDE([Sales Amount], CALCULATE([Sales Amount], ALLEXCEPT(Products, Products[Category])))
```

### Product Rank

```dax
IF(HASONEVALUE(Products[Product]), RANKX(ALL(Products), [Sales Amount], , DESC, DENSE))
```

### Top 5 Products Sales

```dax
CALCULATE([Sales Amount], TOPN(5, ALL(Products), [Sales Amount], DESC))
```

## 4. Target

### Sales Target

```dax
CALCULATE(
    SUM(Targets[TargetAmount]),
    TREATAS(VALUES('Date'[Month Start]), Targets[MonthStart]),
    TREATAS(VALUES(Stores[Region]), Targets[Region])
)
```

### Sales vs Target %

```dax
DIVIDE([Sales Amount], [Sales Target])
```

### Target Status

```dax
VAR _p = [Sales vs Target %]
RETURN SWITCH(TRUE(), ISBLANK(_p), BLANK(), _p >= 1, "On target", _p >= 0.9, "Close", "Below target")
```

## 5. HTML

### HTML KPI Cards

```dax
VAR _sales = [Sales Amount]
VAR _margin = [Gross Margin %]
VAR _yoy = [Sales YoY %]
VAR _vsTarget = [Sales vs Target %]
VAR _green = "#1B9E5A"
VAR _amber = "#E0A100"
VAR _red = "#D64545"
VAR _yoyColor = IF(_yoy >= 0, _green, _red)
VAR _yoyArrow = IF(_yoy >= 0, "&#9650;", "&#9660;")
VAR _tgtColor = SWITCH(TRUE(), _vsTarget >= 1, _green, _vsTarget >= 0.9, _amber, _red)
VAR _card = "flex:1;margin:6px;padding:14px 16px;background:#FFFFFF;border-radius:10px;border:1px solid #D6DBE4;border-top:5px solid "
VAR _label = "<div style='font:600 13px Segoe UI;color:#5B6475;text-transform:uppercase;letter-spacing:.5px'>"
VAR _value = "<div style='font:700 30px Segoe UI;color:#14213D;margin-top:6px'>"
VAR _sub = "<div style='font:13px Segoe UI;margin-top:4px;color:"
RETURN
"<div style='display:flex;font-family:Segoe UI'>"
    & "<div style='" & _card & "#0F57FF'>" & _label & "Revenue</div>" & _value & FORMAT(_sales, "$#,0") & "</div>"
    & _sub & "#5B6475'>" & FORMAT([Orders], "#,0") & " orders &middot; AOV " & FORMAT([Avg Order Value], "$#,0") & "</div></div>"
    & "<div style='" & _card & "#7A4DFF'>" & _label & "Gross margin</div>" & _value & FORMAT(_margin, "0.0%") & "</div>"
    & _sub & "#5B6475'>" & FORMAT([Gross Margin], "$#,0") & " margin</div></div>"
    & "<div style='" & _card & _yoyColor & "'>" & _label & "YoY growth</div>" & _value
    & "<span style='color:" & _yoyColor & "'>" & _yoyArrow & " " & IF(ISBLANK(_yoy), "n/a", FORMAT(_yoy, "+0.0%;-0.0%")) & "</span></div>"
    & _sub & "#5B6475'>Latest year vs same period last year</div></div>"
    & "<div style='" & _card & _tgtColor & "'>" & _label & "Sales vs target</div>" & _value
    & "<span style='color:" & _tgtColor & "'>" & FORMAT(_vsTarget, "0.0%") & "</span></div>"
    & _sub & _tgtColor & "'>" & [Target Status] & "</div></div>"
& "</div>"
```

### HTML Region Progress

```dax
VAR _rows =
    CONCATENATEX(
        VALUES(Stores[Region]),
        VAR _pct = [Sales vs Target %]
        VAR _w = MIN(_pct, 1.2) / 1.2 * 100
        VAR _c = SWITCH(TRUE(), _pct >= 1, "#1B9E5A", _pct >= 0.9, "#E0A100", "#D64545")
        RETURN
        "<div style='margin:10px 0'>"
            & "<div style='display:flex;justify-content:space-between;font:600 14px Segoe UI;color:#14213D'>"
            & "<span>" & Stores[Region] & "</span><span style='color:" & _c & "'>" & FORMAT(_pct, "0.0%") & "</span></div>"
            & "<div style='position:relative;height:12px;background:#E9EDF3;border-radius:6px;margin-top:4px'>"
            & "<div style='width:" & FORMAT(_w, "0") & "%;height:12px;background:" & _c & ";border-radius:6px'></div>"
            & "<div style='position:absolute;left:83.3%;top:-3px;width:2px;height:18px;background:#14213D'></div>"
            & "</div>"
            & "<div style='font:12px Segoe UI;color:#5B6475;margin-top:2px'>" & FORMAT([Sales Amount], "$#,0") & " of " & FORMAT([Sales Target], "$#,0") & " target</div>"
        & "</div>",
        "",
        [Sales vs Target %], DESC
    )
RETURN
"<div style='font-family:Segoe UI;padding:4px 8px'>"
    & "<div style='font:700 16px Segoe UI;color:#14213D'>Revenue vs target by region</div>"
    & "<div style='font:12px Segoe UI;color:#5B6475'>Dark line = 100% of target</div>"
    & _rows
& "</div>"
```

### HTML Top Products

```dax
VAR _top = TOPN(5, ALL(Products[Product]), [Sales Amount], DESC)
VAR _max = MAXX(_top, [Sales Amount])
VAR _rows =
    CONCATENATEX(
        _top,
        VAR _s = [Sales Amount]
        RETURN
        "<div style='display:flex;align-items:center;margin:8px 0;font:14px Segoe UI;color:#14213D'>"
            & "<div style='width:26px;height:26px;border-radius:13px;background:#0F57FF;color:#FFFFFF;font-weight:700;display:flex;align-items:center;justify-content:center;margin-right:10px'>"
            & RANKX(_top, [Sales Amount], , DESC) & "</div>"
            & "<div style='flex:1'><div style='display:flex;justify-content:space-between'><span>" & Products[Product] & "</span><b>" & FORMAT(_s, "$#,0") & "</b></div>"
            & "<div style='height:6px;background:#E9EDF3;border-radius:3px;margin-top:3px'><div style='width:" & FORMAT(DIVIDE(_s, _max) * 100, "0") & "%;height:6px;background:#0F57FF;border-radius:3px'></div></div></div>"
        & "</div>",
        "",
        [Sales Amount], DESC
    )
RETURN
"<div style='font-family:Segoe UI;padding:4px 8px'>"
    & "<div style='font:700 16px Segoe UI;color:#14213D'>Top 5 products</div>"
    & _rows
& "</div>"
```
