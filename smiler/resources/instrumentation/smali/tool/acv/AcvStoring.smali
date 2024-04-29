.class public Ltool/acv/AcvStoring;
.super Ljava/lang/Object;
.source "AcvStoring.java"


# instance fields
.field private counter:I

.field private snapTime:Ljava/lang/String;


# direct methods
.method public constructor <init>()V
    .locals 1

    .line 12
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    const/4 v0, 0x0

    .line 14
    iput v0, p0, Ltool/acv/AcvStoring;->counter:I

    return-void
.end method

.method private saveExternalPublicFile([Ljava/lang/reflect/Field;)V
    .locals 5

    .line 23
    invoke-static {p1}, Ltool/acv/AcvReporterFields;->fieldsToArray([Ljava/lang/reflect/Field;)[[Z

    move-result-object p1

    .line 24
    invoke-virtual {p0}, Ltool/acv/AcvStoring;->getCoverageFilename()Ljava/lang/String;

    move-result-object v0

    .line 25
    new-instance v1, Ljava/io/File;

    invoke-direct {v1, v0}, Ljava/io/File;-><init>(Ljava/lang/String;)V

    const/4 v2, 0x1

    const/4 v3, 0x0

    .line 26
    invoke-virtual {v1, v2, v3}, Ljava/io/File;->setReadable(ZZ)Z

    const-string v2, "ACV"

    .line 29
    :try_start_0
    new-instance v3, Ljava/io/ObjectOutputStream;

    new-instance v4, Ljava/io/FileOutputStream;

    invoke-direct {v4, v1}, Ljava/io/FileOutputStream;-><init>(Ljava/io/File;)V

    invoke-direct {v3, v4}, Ljava/io/ObjectOutputStream;-><init>(Ljava/io/OutputStream;)V

    .line 30
    invoke-virtual {v3, p1}, Ljava/io/ObjectOutputStream;->writeObject(Ljava/lang/Object;)V

    .line 31
    invoke-virtual {v3}, Ljava/io/ObjectOutputStream;->flush()V

    .line 32
    invoke-virtual {v3}, Ljava/io/ObjectOutputStream;->close()V

    .line 33
    invoke-static {v2, v0}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I
    :try_end_0
    .catch Ljava/io/IOException; {:try_start_0 .. :try_end_0} :catch_0

    goto :goto_0

    :catch_0
    move-exception p1

    .line 35
    invoke-virtual {p1}, Ljava/io/IOException;->printStackTrace()V

    .line 36
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v1, ":saving: "

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p1}, Ljava/io/IOException;->getMessage()Ljava/lang/String;

    move-result-object p1

    invoke-virtual {v0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p1

    invoke-static {v2, p1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I

    :goto_0
    return-void
.end method


# virtual methods
.method public getCoverageFilename()Ljava/lang/String;
    .locals 2

    .line 18
    iget v0, p0, Ltool/acv/AcvStoring;->counter:I

    add-int/lit8 v0, v0, 0x1

    iput v0, p0, Ltool/acv/AcvStoring;->counter:I

    .line 19
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v1, "/sdcard/Download/app.debloat.instrapp/coverage_"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    iget-object v1, p0, Ltool/acv/AcvStoring;->snapTime:Ljava/lang/String;

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const/16 v1, 0x5f

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;

    iget v1, p0, Ltool/acv/AcvStoring;->counter:I

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    const-string v1, ".ec"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    return-object v0
.end method

.method public saveCoverage()V
    .locals 2

    const/4 v0, 0x0

    .line 43
    iput v0, p0, Ltool/acv/AcvStoring;->counter:I

    .line 44
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v0

    invoke-static {v0, v1}, Ljava/lang/String;->valueOf(J)Ljava/lang/String;

    move-result-object v0

    iput-object v0, p0, Ltool/acv/AcvStoring;->snapTime:Ljava/lang/String;

    .line 45
    const-class v0, Ltool/acv/AcvReporter1;

    invoke-virtual {v0}, Ljava/lang/Class;->getFields()[Ljava/lang/reflect/Field;

    move-result-object v0

    .line 46
    invoke-direct {p0, v0}, Ltool/acv/AcvStoring;->saveExternalPublicFile([Ljava/lang/reflect/Field;)V
# additional code starts here
