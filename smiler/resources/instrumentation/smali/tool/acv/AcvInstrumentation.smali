.class public Ltool/acv/AcvInstrumentation;
.super Landroid/app/Instrumentation;
.source "acvinstrumentation.java"


# static fields
.field private static final ACTION_FINISH_TESTING:Ljava/lang/String; = "tool.acv.finishtesting"

.field private static final DEFAULT_REPORT_ROOTDIR:Ljava/lang/String; = "/mnt/sdcard"

.field private static final ERRORS_FILENAME:Ljava/lang/String; = "errors.txt"

.field private static final KEY_CANCEL_ANALYSIS:Ljava/lang/String; = "cancelAnalysis"

.field private static final KEY_COVERAGE:Ljava/lang/String; = "coverage"

.field private static final KEY_GENERATE_COVERAGE_REPORT_ON_ERROR:Ljava/lang/String; = "generateCoverageReportOnError"

.field private static final KEY_PROCEED_ON_ERROR:Ljava/lang/String; = "proceedOnError"

.field private static final KEY_REPORT_FOLDER:Ljava/lang/String; = "coverageDir"

.field private static final MSG_FINISH_INSTRUMENTATION:I = 0xb

.field private static final MSG_FINISH_WRITER_OPERATIONS:I = 0x4

.field private static final MSG_GENERATE_COVERAGE:I = 0x1

.field private static final MSG_REMOVE_REPORT_DIR:I = 0x3

.field private static final MSG_REPORT_EXCEPTION:I = 0x2

.field private static final PREFIX_ONERROR:Ljava/lang/String; = "onerror"

.field private static final PREFIX_ONSTOP:Ljava/lang/String; = "onstop"

.field private static final TAG:Ljava/lang/String; = "AcvInstrumentation"

.field private static errorCounter:I

.field private static targetPackageName:Ljava/lang/String;


# instance fields
.field private cancelAnalysis:Z

.field private errorFile:Ljava/io/File;

.field private generateCoverageOnError:Z

.field private ht:Landroid/os/HandlerThread;

.field private lockFile:Ljava/io/File;

.field private mCoverage:Z

.field private final mMessageReceiver:Landroid/content/BroadcastReceiver;

.field private mUiHandler:Landroid/os/Handler;

.field private mWriterThreadHandler:Landroid/os/Handler;

.field private proceedOnError:Z

.field private reportDir:Ljava/io/File;

.field private final uiThreadHandlerCallback:Landroid/os/Handler$Callback;

.field private final writerThreadHandlerCallback:Landroid/os/Handler$Callback;


# direct methods
.method static constructor <clinit>()V
    .locals 1

    .prologue
    .line 67
    const/4 v0, 0x0

    sput v0, Ltool/acv/AcvInstrumentation;->errorCounter:I

    return-void
.end method

.method public constructor <init>()V
    .locals 3

    .prologue
    const/4 v2, 0x1

    const/4 v1, 0x0

    const/4 v0, 0x0

    .line 78
    invoke-direct {p0}, Landroid/app/Instrumentation;-><init>()V

    .line 58
    iput-boolean v2, p0, Ltool/acv/AcvInstrumentation;->mCoverage:Z

    .line 59
    iput-boolean v2, p0, Ltool/acv/AcvInstrumentation;->generateCoverageOnError:Z

    .line 60
    iput-boolean v1, p0, Ltool/acv/AcvInstrumentation;->proceedOnError:Z

    .line 61
    iput-boolean v1, p0, Ltool/acv/AcvInstrumentation;->cancelAnalysis:Z

    .line 63
    iput-object v0, p0, Ltool/acv/AcvInstrumentation;->reportDir:Ljava/io/File;

    .line 64
    iput-object v0, p0, Ltool/acv/AcvInstrumentation;->errorFile:Ljava/io/File;

    .line 65
    iput-object v0, p0, Ltool/acv/AcvInstrumentation;->lockFile:Ljava/io/File;

    .line 250
    new-instance v0, Ltool/acv/AcvInstrumentation$1;

    invoke-direct {v0, p0}, Ltool/acv/AcvInstrumentation$1;-><init>(Ltool/acv/AcvInstrumentation;)V

    iput-object v0, p0, Ltool/acv/AcvInstrumentation;->mMessageReceiver:Landroid/content/BroadcastReceiver;

    .line 284
    new-instance v0, Ltool/acv/AcvInstrumentation$2;

    invoke-direct {v0, p0}, Ltool/acv/AcvInstrumentation$2;-><init>(Ltool/acv/AcvInstrumentation;)V

    iput-object v0, p0, Ltool/acv/AcvInstrumentation;->uiThreadHandlerCallback:Landroid/os/Handler$Callback;

    .line 301
    new-instance v0, Ltool/acv/AcvInstrumentation$3;

    invoke-direct {v0, p0}, Ltool/acv/AcvInstrumentation$3;-><init>(Ltool/acv/AcvInstrumentation;)V

    iput-object v0, p0, Ltool/acv/AcvInstrumentation;->writerThreadHandlerCallback:Landroid/os/Handler$Callback;

    .line 80
    return-void
.end method

.method static synthetic access$000(Ltool/acv/AcvInstrumentation;)Z
    .locals 1

    .prologue
    .line 31
    iget-boolean v0, p0, Ltool/acv/AcvInstrumentation;->cancelAnalysis:Z

    return v0
.end method

.method static synthetic access$002(Ltool/acv/AcvInstrumentation;Z)Z
    .locals 0

    .prologue
    .line 31
    iput-boolean p1, p0, Ltool/acv/AcvInstrumentation;->cancelAnalysis:Z

    return p1
.end method

.method static synthetic access$100(Ltool/acv/AcvInstrumentation;)Landroid/os/Handler;
    .locals 1

    .prologue
    .line 31
    iget-object v0, p0, Ltool/acv/AcvInstrumentation;->mWriterThreadHandler:Landroid/os/Handler;

    return-object v0
.end method

.method static synthetic access$200(Ltool/acv/AcvInstrumentation;)Z
    .locals 1

    .prologue
    .line 31
    iget-boolean v0, p0, Ltool/acv/AcvInstrumentation;->mCoverage:Z

    return v0
.end method

.method static synthetic access$300(Ltool/acv/AcvInstrumentation;ILjava/lang/String;)V
    .locals 0

    .prologue
    .line 31
    invoke-direct {p0, p1, p2}, Ltool/acv/AcvInstrumentation;->finish(ILjava/lang/String;)V

    return-void
.end method

.method static synthetic access$400(Ltool/acv/AcvInstrumentation;)Ljava/io/File;
    .locals 1

    .prologue
    .line 31
    iget-object v0, p0, Ltool/acv/AcvInstrumentation;->reportDir:Ljava/io/File;

    return-object v0
.end method

.method static synthetic access$500(Ltool/acv/AcvInstrumentation;)Landroid/os/Handler;
    .locals 1

    .prologue
    .line 31
    iget-object v0, p0, Ltool/acv/AcvInstrumentation;->mUiHandler:Landroid/os/Handler;

    return-object v0
.end method

.method static synthetic access$600(Ltool/acv/AcvInstrumentation;)Ljava/io/File;
    .locals 1

    .prologue
    .line 31
    iget-object v0, p0, Ltool/acv/AcvInstrumentation;->errorFile:Ljava/io/File;

    return-object v0
.end method

.method private compileExceptionMessage(JLjava/lang/String;Ljava/lang/Object;Ljava/lang/Throwable;)Ljava/lang/String;
    .locals 7

    .prologue
    .line 189
    if-nez p4, :cond_1

    .line 190
    const-string v0, "null"

    .line 208
    :goto_0
    const-string v1, "null"

    .line 209
    if-eqz p4, :cond_0

    .line 210
    invoke-virtual {p4}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/Class;->getName()Ljava/lang/String;

    move-result-object v1

    .line 213
    :cond_0
    new-instance v2, Ljava/lang/StringBuffer;

    invoke-direct {v2}, Ljava/lang/StringBuffer;-><init>()V

    .line 214
    const-string v3, "ErrorCount: "

    invoke-virtual {v2, v3}, Ljava/lang/StringBuffer;->append(Ljava/lang/String;)Ljava/lang/StringBuffer;

    move-result-object v3

    sget v4, Ltool/acv/AcvInstrumentation;->errorCounter:I

    add-int/lit8 v5, v4, 0x1

    sput v5, Ltool/acv/AcvInstrumentation;->errorCounter:I

    invoke-virtual {v3, v4}, Ljava/lang/StringBuffer;->append(I)Ljava/lang/StringBuffer;

    move-result-object v3

    const-string v4, "\n"

    invoke-virtual {v3, v4}, Ljava/lang/StringBuffer;->append(Ljava/lang/String;)Ljava/lang/StringBuffer;

    .line 215
    const-string v3, "Time: "

    invoke-virtual {v2, v3}, Ljava/lang/StringBuffer;->append(Ljava/lang/String;)Ljava/lang/StringBuffer;

    move-result-object v3

    invoke-virtual {v3, p1, p2}, Ljava/lang/StringBuffer;->append(J)Ljava/lang/StringBuffer;

    move-result-object v3

    const-string v4, "\n"

    invoke-virtual {v3, v4}, Ljava/lang/StringBuffer;->append(Ljava/lang/String;)Ljava/lang/StringBuffer;

    .line 216
    const-string v3, "CoverageFile: "

    invoke-virtual {v2, v3}, Ljava/lang/StringBuffer;->append(Ljava/lang/String;)Ljava/lang/StringBuffer;

    move-result-object v3

    if-eqz p3, :cond_6

    :goto_1
    invoke-virtual {v3, p3}, Ljava/lang/StringBuffer;->append(Ljava/lang/String;)Ljava/lang/StringBuffer;

    move-result-object v3

    const-string v4, "\n"

    invoke-virtual {v3, v4}, Ljava/lang/StringBuffer;->append(Ljava/lang/String;)Ljava/lang/StringBuffer;

    .line 217
    const-string v3, "PackageName: "

    invoke-virtual {v2, v3}, Ljava/lang/StringBuffer;->append(Ljava/lang/String;)Ljava/lang/StringBuffer;

    move-result-object v3

    sget-object v4, Ltool/acv/AcvInstrumentation;->targetPackageName:Ljava/lang/String;

    invoke-virtual {v3, v4}, Ljava/lang/StringBuffer;->append(Ljava/lang/String;)Ljava/lang/StringBuffer;

    move-result-object v3

    const-string v4, "\n"

    invoke-virtual {v3, v4}, Ljava/lang/StringBuffer;->append(Ljava/lang/String;)Ljava/lang/StringBuffer;

    .line 219
    const-string v3, "ErrorComponent: "

    invoke-virtual {v2, v3}, Ljava/lang/StringBuffer;->append(Ljava/lang/String;)Ljava/lang/StringBuffer;

    move-result-object v3

    invoke-virtual {v3, v0}, Ljava/lang/StringBuffer;->append(Ljava/lang/String;)Ljava/lang/StringBuffer;

    move-result-object v0

    const-string v3, "\n"

    invoke-virtual {v0, v3}, Ljava/lang/StringBuffer;->append(Ljava/lang/String;)Ljava/lang/StringBuffer;

    .line 220
    const-string v0, "ErrorSource: "

    invoke-virtual {v2, v0}, Ljava/lang/StringBuffer;->append(Ljava/lang/String;)Ljava/lang/StringBuffer;

    move-result-object v0

    invoke-virtual {v0, v1}, Ljava/lang/StringBuffer;->append(Ljava/lang/String;)Ljava/lang/StringBuffer;

    move-result-object v0

    const-string v1, "\n"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuffer;->append(Ljava/lang/String;)Ljava/lang/StringBuffer;

    .line 221
    const-string v0, "ShortMsg: "

    invoke-virtual {v2, v0}, Ljava/lang/StringBuffer;->append(Ljava/lang/String;)Ljava/lang/StringBuffer;

    move-result-object v0

    invoke-virtual {p5}, Ljava/lang/Throwable;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Ljava/lang/StringBuffer;->append(Ljava/lang/String;)Ljava/lang/StringBuffer;

    move-result-object v0

    const-string v1, "\n"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuffer;->append(Ljava/lang/String;)Ljava/lang/StringBuffer;

    .line 222
    const-string v0, "LongMsg: "

    invoke-virtual {v2, v0}, Ljava/lang/StringBuffer;->append(Ljava/lang/String;)Ljava/lang/StringBuffer;

    move-result-object v0

    invoke-virtual {p5}, Ljava/lang/Throwable;->getMessage()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Ljava/lang/StringBuffer;->append(Ljava/lang/String;)Ljava/lang/StringBuffer;

    move-result-object v0

    const-string v1, "\n"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuffer;->append(Ljava/lang/String;)Ljava/lang/StringBuffer;

    .line 223
    const-string v0, "Stack: \n"

    invoke-virtual {v2, v0}, Ljava/lang/StringBuffer;->append(Ljava/lang/String;)Ljava/lang/StringBuffer;

    move-result-object v0

    invoke-direct {p0, p5}, Ltool/acv/AcvInstrumentation;->getStackTrace(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Ljava/lang/StringBuffer;->append(Ljava/lang/String;)Ljava/lang/StringBuffer;

    move-result-object v0

    const-string v1, "\n"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuffer;->append(Ljava/lang/String;)Ljava/lang/StringBuffer;

    .line 226
    const-string v0, "============================================================"

    invoke-virtual {v2, v0}, Ljava/lang/StringBuffer;->append(Ljava/lang/String;)Ljava/lang/StringBuffer;

    move-result-object v0

    const-string v1, "\n\n"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuffer;->append(Ljava/lang/String;)Ljava/lang/StringBuffer;

    .line 228
    invoke-virtual {v2}, Ljava/lang/StringBuffer;->toString()Ljava/lang/String;

    move-result-object v0

    return-object v0

    .line 192
    :cond_1
    instance-of v0, p4, Landroid/app/Application;

    if-eqz v0, :cond_2

    .line 193
    const-string v0, "Application"

    goto/16 :goto_0

    .line 195
    :cond_2
    instance-of v0, p4, Landroid/app/Activity;

    if-eqz v0, :cond_3

    .line 196
    const-string v0, "Activity"

    goto/16 :goto_0

    .line 198
    :cond_3
    instance-of v0, p4, Landroid/app/Service;

    if-eqz v0, :cond_4

    .line 199
    const-string v0, "Service"

    goto/16 :goto_0

    .line 201
    :cond_4
    instance-of v0, p4, Landroid/content/BroadcastReceiver;

    if-eqz v0, :cond_5

    .line 202
    const-string v0, "BroadcastReceiver"

    goto/16 :goto_0

    .line 205
    :cond_5
    invoke-virtual {p4}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/Class;->getSimpleName()Ljava/lang/String;

    move-result-object v0

    goto/16 :goto_0

    .line 216
    :cond_6
    const-string p3, ""

    goto/16 :goto_1
.end method

.method private finish(ILjava/lang/String;)V
    .locals 3

    .prologue
    .line 160
    new-instance v0, Landroid/os/Bundle;

    invoke-direct {v0}, Landroid/os/Bundle;-><init>()V

    .line 161
    const-string v1, "id"

    const-class v2, Ltool/acv/AcvInstrumentation;

    invoke-virtual {v2}, Ljava/lang/Class;->getName()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v0, v1, v2}, Landroid/os/Bundle;->putString(Ljava/lang/String;Ljava/lang/String;)V

    .line 162
    const-string v1, "stream"

    invoke-virtual {v0, v1, p2}, Landroid/os/Bundle;->putString(Ljava/lang/String;Ljava/lang/String;)V

    .line 163
    invoke-virtual {p0, p1, v0}, Ltool/acv/AcvInstrumentation;->finish(ILandroid/os/Bundle;)V

    .line 164
    return-void
.end method

.method private getBooleanArgument(Landroid/os/Bundle;Ljava/lang/String;Z)Z
    .locals 1

    .prologue
    .line 241
    invoke-virtual {p1, p2}, Landroid/os/Bundle;->getString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    .line 242
    if-nez v0, :cond_0

    :goto_0
    return p3

    :cond_0
    invoke-static {v0}, Ljava/lang/Boolean;->parseBoolean(Ljava/lang/String;)Z

    move-result p3

    goto :goto_0
.end method

.method private getStackTrace(Ljava/lang/Throwable;)Ljava/lang/String;
    .locals 2

    .prologue
    .line 233
    new-instance v0, Ljava/io/StringWriter;

    invoke-direct {v0}, Ljava/io/StringWriter;-><init>()V

    .line 234
    new-instance v1, Ljava/io/PrintWriter;

    invoke-direct {v1, v0}, Ljava/io/PrintWriter;-><init>(Ljava/io/Writer;)V

    .line 235
    invoke-virtual {p1, v1}, Ljava/lang/Throwable;->printStackTrace(Ljava/io/PrintWriter;)V

    .line 236
    invoke-virtual {v0}, Ljava/io/StringWriter;->toString()Ljava/lang/String;

    move-result-object v0

    return-object v0
.end method


# virtual methods
.method public finish(ILandroid/os/Bundle;)V
    .locals 3

    .prologue
    .line 169
    const-string v0, "AcvInstrumentation"

    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "Finishing instrumentation. ResultCode: "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, p1}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, " Results: "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {p2}, Landroid/os/Bundle;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I

    .line 170
    iget-object v0, p0, Ltool/acv/AcvInstrumentation;->lockFile:Ljava/io/File;

    if-eqz v0, :cond_0

    iget-object v0, p0, Ltool/acv/AcvInstrumentation;->lockFile:Ljava/io/File;

    invoke-virtual {v0}, Ljava/io/File;->exists()Z

    move-result v0

    if-eqz v0, :cond_0

    .line 171
    const-string v0, "AcvInstrumentation"

    const-string v1, "finish: Removing lockFile..."

    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I

    .line 172
    iget-object v0, p0, Ltool/acv/AcvInstrumentation;->lockFile:Ljava/io/File;

    invoke-virtual {v0}, Ljava/io/File;->delete()Z

    .line 174
    :cond_0
    invoke-super {p0, p1, p2}, Landroid/app/Instrumentation;->finish(ILandroid/os/Bundle;)V

    .line 175
    return-void
.end method

.method public onCreate(Landroid/os/Bundle;)V
    .locals 5

    .prologue
    const/4 v3, 0x1

    const/4 v4, 0x0

    .line 84
    invoke-super {p0, p1}, Landroid/app/Instrumentation;->onCreate(Landroid/os/Bundle;)V

    .line 85
    const-string v0, "AcvInstrumentation"

    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "onCreate: Obtained instrumentation intent: "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {p1}, Landroid/os/Bundle;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I

    .line 88
    invoke-virtual {p0}, Ltool/acv/AcvInstrumentation;->getComponentName()Landroid/content/ComponentName;

    move-result-object v0

    invoke-virtual {v0}, Landroid/content/ComponentName;->getPackageName()Ljava/lang/String;

    move-result-object v0

    sput-object v0, Ltool/acv/AcvInstrumentation;->targetPackageName:Ljava/lang/String;

    .line 90
    const-string v0, "coverage"

    invoke-direct {p0, p1, v0, v3}, Ltool/acv/AcvInstrumentation;->getBooleanArgument(Landroid/os/Bundle;Ljava/lang/String;Z)Z

    move-result v0

    iput-boolean v0, p0, Ltool/acv/AcvInstrumentation;->mCoverage:Z

    .line 91
    const-string v0, "proceedOnError"

    invoke-direct {p0, p1, v0, v3}, Ltool/acv/AcvInstrumentation;->getBooleanArgument(Landroid/os/Bundle;Ljava/lang/String;Z)Z

    move-result v0

    iput-boolean v0, p0, Ltool/acv/AcvInstrumentation;->proceedOnError:Z

    .line 92
    const-string v0, "generateCoverageReportOnError"

    invoke-direct {p0, p1, v0, v4}, Ltool/acv/AcvInstrumentation;->getBooleanArgument(Landroid/os/Bundle;Ljava/lang/String;Z)Z

    move-result v0

    iput-boolean v0, p0, Ltool/acv/AcvInstrumentation;->generateCoverageOnError:Z

    .line 94
    const-string v0, "coverageDir"

    const-string v1, "/mnt/sdcard"

    invoke-virtual {p1, v0, v1}, Landroid/os/Bundle;->getString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    .line 96
    new-instance v0, Ljava/io/File;

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    sget-object v3, Ltool/acv/AcvInstrumentation;->targetPackageName:Ljava/lang/String;

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    const-string v3, ".lock"

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-direct {v0, v1, v2}, Ljava/io/File;-><init>(Ljava/lang/String;Ljava/lang/String;)V

    iput-object v0, p0, Ltool/acv/AcvInstrumentation;->lockFile:Ljava/io/File;

    .line 97
    iget-object v0, p0, Ltool/acv/AcvInstrumentation;->lockFile:Ljava/io/File;

    invoke-virtual {v0}, Ljava/io/File;->exists()Z

    move-result v0

    if-nez v0, :cond_0

    .line 99
    :try_start_0
    iget-object v0, p0, Ltool/acv/AcvInstrumentation;->lockFile:Ljava/io/File;

    invoke-virtual {v0}, Ljava/io/File;->createNewFile()Z
    :try_end_0
    .catch Ljava/io/IOException; {:try_start_0 .. :try_end_0} :catch_0

    .line 111
    :goto_0
    new-instance v0, Ljava/io/File;

    iget-object v2, p0, Ltool/acv/AcvInstrumentation;->reportDir:Ljava/io/File;

    const-string v3, "errors.txt"

    invoke-direct {v0, v2, v3}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    iput-object v0, p0, Ltool/acv/AcvInstrumentation;->errorFile:Ljava/io/File;

    .line 112
    new-instance v0, Ljava/io/File;

    sget-object v2, Ltool/acv/AcvInstrumentation;->targetPackageName:Ljava/lang/String;

    invoke-direct {v0, v1, v2}, Ljava/io/File;-><init>(Ljava/lang/String;Ljava/lang/String;)V

    iput-object v0, p0, Ltool/acv/AcvInstrumentation;->reportDir:Ljava/io/File;

    .line 113
    iget-object v0, p0, Ltool/acv/AcvInstrumentation;->reportDir:Ljava/io/File;

    invoke-virtual {v0}, Ljava/io/File;->mkdirs()Z

    move-result v0

    .line 114
    const-string v1, "AcvInstrumentation"

    if-eqz v0, :cond_1

    const-string v0, "The report dir is created!"

    :goto_1
    invoke-static {v1, v0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 116
    new-instance v0, Landroid/os/HandlerThread;

    const-string v1, "WriterThread"

    invoke-direct {v0, v1}, Landroid/os/HandlerThread;-><init>(Ljava/lang/String;)V

    iput-object v0, p0, Ltool/acv/AcvInstrumentation;->ht:Landroid/os/HandlerThread;

    .line 117
    iget-object v0, p0, Ltool/acv/AcvInstrumentation;->ht:Landroid/os/HandlerThread;

    invoke-virtual {v0}, Landroid/os/HandlerThread;->start()V

    .line 118
    new-instance v0, Landroid/os/Handler;

    iget-object v1, p0, Ltool/acv/AcvInstrumentation;->ht:Landroid/os/HandlerThread;

    invoke-virtual {v1}, Landroid/os/HandlerThread;->getLooper()Landroid/os/Looper;

    move-result-object v1

    iget-object v2, p0, Ltool/acv/AcvInstrumentation;->writerThreadHandlerCallback:Landroid/os/Handler$Callback;

    invoke-direct {v0, v1, v2}, Landroid/os/Handler;-><init>(Landroid/os/Looper;Landroid/os/Handler$Callback;)V

    iput-object v0, p0, Ltool/acv/AcvInstrumentation;->mWriterThreadHandler:Landroid/os/Handler;

    .line 119
    new-instance v0, Landroid/os/Handler;

    iget-object v1, p0, Ltool/acv/AcvInstrumentation;->uiThreadHandlerCallback:Landroid/os/Handler$Callback;

    invoke-direct {v0, v1}, Landroid/os/Handler;-><init>(Landroid/os/Handler$Callback;)V

    iput-object v0, p0, Ltool/acv/AcvInstrumentation;->mUiHandler:Landroid/os/Handler;

    .line 121
    new-instance v0, Landroid/content/IntentFilter;

    const-string v1, "tool.acv.finishtesting"

    invoke-direct {v0, v1}, Landroid/content/IntentFilter;-><init>(Ljava/lang/String;)V

    .line 122
    invoke-virtual {p0}, Ltool/acv/AcvInstrumentation;->getContext()Landroid/content/Context;

    move-result-object v1

    iget-object v2, p0, Ltool/acv/AcvInstrumentation;->mMessageReceiver:Landroid/content/BroadcastReceiver;

    invoke-virtual {v1, v2, v0}, Landroid/content/Context;->registerReceiver(Landroid/content/BroadcastReceiver;Landroid/content/IntentFilter;)Landroid/content/Intent;

    .line 124
    invoke-virtual {p0}, Ltool/acv/AcvInstrumentation;->start()V

    .line 125
    const-string v0, "AcvInstrumentation"

    const-string v1, "onCreate: After start!"

    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I

    .line 126
    :goto_2
    return-void

    .line 100
    :catch_0
    move-exception v0

    .line 102
    invoke-virtual {v0}, Ljava/io/IOException;->printStackTrace()V

    goto :goto_0

    .line 106
    :cond_0
    const-string v0, "AcvInstrumentation"

    const-string v1, "Lock file exists for some reason. Exiting instrumentation!"

    invoke-static {v0, v1}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I

    .line 107
    const-string v0, "Lock file exists for some reason. Exiting instrumentation!"

    invoke-direct {p0, v4, v0}, Ltool/acv/AcvInstrumentation;->finish(ILjava/lang/String;)V

    goto :goto_2

    .line 114
    :cond_1
    const-string v0, "The report dir is NOT created!"

    goto :goto_1
.end method

.method public onDestroy()V
    .locals 3

    .prologue
    .line 180
    const-string v0, "AcvInstrumentation"

    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "OnDestroy. Thread: "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-static {}, Ljava/lang/Thread;->currentThread()Ljava/lang/Thread;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/Thread;->getName()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I

    .line 181
    invoke-virtual {p0}, Ltool/acv/AcvInstrumentation;->getContext()Landroid/content/Context;

    move-result-object v0

    iget-object v1, p0, Ltool/acv/AcvInstrumentation;->mMessageReceiver:Landroid/content/BroadcastReceiver;

    invoke-virtual {v0, v1}, Landroid/content/Context;->unregisterReceiver(Landroid/content/BroadcastReceiver;)V

    .line 182
    iget-object v0, p0, Ltool/acv/AcvInstrumentation;->ht:Landroid/os/HandlerThread;

    invoke-virtual {v0}, Landroid/os/HandlerThread;->getLooper()Landroid/os/Looper;

    move-result-object v0

    invoke-virtual {v0}, Landroid/os/Looper;->quitSafely()V

    .line 183
    invoke-super {p0}, Landroid/app/Instrumentation;->onDestroy()V

    .line 184
    return-void
.end method

.method public onException(Ljava/lang/Object;Ljava/lang/Throwable;)Z
    .locals 7

    .prologue
    .line 139
    const-string v0, "AcvInstrumentation"

    const-string v1, "onException: AUT exception caught!"

    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I

    .line 141
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v2

    .line 142
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v1, "onerror_coverage_"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-static {v2, v3}, Ljava/lang/String;->valueOf(J)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, ".ec"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v4

    .line 144
    iget-boolean v0, p0, Ltool/acv/AcvInstrumentation;->generateCoverageOnError:Z

    if-eqz v0, :cond_0

    .line 145
    iget-object v0, p0, Ltool/acv/AcvInstrumentation;->mWriterThreadHandler:Landroid/os/Handler;

    const/4 v1, 0x1

    invoke-static {v0, v1}, Landroid/os/Message;->obtain(Landroid/os/Handler;I)Landroid/os/Message;

    move-result-object v0

    .line 146
    iput-object v4, v0, Landroid/os/Message;->obj:Ljava/lang/Object;

    .line 147
    invoke-virtual {v0}, Landroid/os/Message;->sendToTarget()V

    .line 150
    :cond_0
    iget-object v0, p0, Ltool/acv/AcvInstrumentation;->mWriterThreadHandler:Landroid/os/Handler;

    const/4 v1, 0x2

    invoke-static {v0, v1}, Landroid/os/Message;->obtain(Landroid/os/Handler;I)Landroid/os/Message;

    move-result-object v0

    move-object v1, p0

    move-object v5, p1

    move-object v6, p2

    .line 151
    invoke-direct/range {v1 .. v6}, Ltool/acv/AcvInstrumentation;->compileExceptionMessage(JLjava/lang/String;Ljava/lang/Object;Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object v1

    iput-object v1, v0, Landroid/os/Message;->obj:Ljava/lang/Object;

    .line 152
    invoke-virtual {v0}, Landroid/os/Message;->sendToTarget()V

    .line 155
    iget-boolean v0, p0, Ltool/acv/AcvInstrumentation;->proceedOnError:Z

    return v0
.end method

.method public onStart()V
    .locals 3

    .prologue
    .line 131
    invoke-super {p0}, Landroid/app/Instrumentation;->onStart()V

    .line 132
    const-string v0, "AcvInstrumentation"

    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "Starting instrumentation. Thread: "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-static {}, Ljava/lang/Thread;->currentThread()Ljava/lang/Thread;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/Thread;->getName()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I

    .line 133
    invoke-static {}, Landroid/os/Looper;->prepare()V

    .line 134
    return-void
.end method
