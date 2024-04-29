.class public final Ltool/acv/AcvReporterFields;
.super Ljava/lang/Object;
.source "AcvReporterFields.java"


# direct methods
.method public constructor <init>()V
    .locals 0

    .line 7
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method public static extractNumber(Ljava/lang/String;)I
    .locals 5

    .line 32
    invoke-virtual {p0}, Ljava/lang/String;->length()I

    move-result v0

    const/4 v1, 0x1

    sub-int/2addr v0, v1

    const/4 v2, 0x0

    .line 33
    :goto_0
    invoke-virtual {p0, v0}, Ljava/lang/String;->charAt(I)C

    move-result v3

    const/16 v4, 0x5f

    if-eq v3, v4, :cond_0

    .line 34
    invoke-virtual {p0, v0}, Ljava/lang/String;->charAt(I)C

    move-result v3

    add-int/lit8 v3, v3, -0x30

    mul-int v3, v3, v1

    add-int/2addr v2, v3

    mul-int/lit8 v1, v1, 0xa

    add-int/lit8 v0, v0, -0x1

    goto :goto_0

    :cond_0
    return v2
.end method

.method public static fieldsToArray([Ljava/lang/reflect/Field;)[[Z
    .locals 5

    .line 15
    array-length v0, p0

    new-array v0, v0, [[Z

    const/4 v1, 0x0

    .line 16
    :goto_0
    array-length v2, p0

    if-ge v1, v2, :cond_0

    .line 18
    :try_start_0
    aget-object v2, p0, v1

    invoke-virtual {v2}, Ljava/lang/reflect/Field;->getName()Ljava/lang/String;

    move-result-object v2

    invoke-static {v2}, Ltool/acv/AcvReporterFields;->extractNumber(Ljava/lang/String;)I

    move-result v2

    .line 19
    aget-object v3, p0, v1

    const/4 v4, 0x0

    invoke-virtual {v3, v4}, Ljava/lang/reflect/Field;->get(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v3

    check-cast v3, [Z

    aput-object v3, v0, v2
    :try_end_0
    .catch Ljava/lang/IllegalAccessException; {:try_start_0 .. :try_end_0} :catch_0

    goto :goto_1

    :catch_0
    move-exception v2

    .line 21
    invoke-virtual {v2}, Ljava/lang/IllegalAccessException;->printStackTrace()V

    .line 22
    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    const-string v4, ":reflection: "

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v2}, Ljava/lang/IllegalAccessException;->getMessage()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v3, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    const-string v3, "ACV"

    invoke-static {v3, v2}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I

    :goto_1
    add-int/lit8 v1, v1, 0x1

    goto :goto_0

    :cond_0
    return-object v0
.end method
