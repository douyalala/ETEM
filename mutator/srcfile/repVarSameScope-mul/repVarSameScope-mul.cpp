//------------------------------------------------------------------------------
// mutation strategy: replace variable
// inputs: first random ori var and random applicable rep var
// usage: repVarSameScope-mul <path to main.c> -- <position>
//------------------------------------------------------------------------------

#include <sstream>
#include <string>
#include <iostream>
#include <map> 
#include <fstream>
#include <memory>
#include <map>
#include <vector>
#include <utility>
#include "clang/AST/AST.h"
#include "clang/AST/ASTConsumer.h"
#include "clang/AST/RecursiveASTVisitor.h"
#include "clang/Frontend/ASTConsumers.h"
#include "clang/Frontend/FrontendActions.h"
#include "clang/Frontend/CompilerInstance.h"
#include "clang/Tooling/CommonOptionsParser.h"
#include "clang/Tooling/Tooling.h"
#include "clang/Rewrite/Core/Rewriter.h"
#include "llvm/Support/raw_ostream.h"
#include "clang/Lex/Lexer.h"
using namespace std;
using namespace clang;
using namespace clang::driver;
using namespace clang::tooling;

static llvm::cl::OptionCategory VisitAST_Category("usage: repVarSameScope-mul <path to main.c> -- <position>");
static int64_t position = -1;

// stage 0: fill the var maps
// stage 1: select the var to rep target var
// stage 2: get the rep var's name
// stage 3: do mutate
static int stage = 0;

static string currFunctionName = "";
static map<string,vector<int>> functionMapVar; // func -- vars in this func
static map<int,string> varMapFunc; // var -- which func this var in

static int currCompoundStmtNum = 0;
static map<string,vector<int>> funcCompoundStmtMapVar; // CompoundStmt -- vars in this CompoundStmt
static map<int,string> varMapFuncCompoundStmt; // var -- which CompoundStmt this var in

static vector<int> varGlobalList;

static int usedtorepVar = 0;
static string usedtorepVarName = "";

class MyASTVisitor : public RecursiveASTVisitor<MyASTVisitor> {
public:
  ASTContext *Context=NULL;
  MyASTVisitor(Rewriter &R) : TheRewriter(R) {}

  bool VisitFunctionDecl(FunctionDecl *f) {
    currFunctionName = f->getNameInfo().getAsString();

    if (stage == 0) {
      vector<int> tmplist;
      pair <string,vector<int>> tmpfunc = make_pair (currFunctionName,tmplist);  
      functionMapVar.insert(tmpfunc);
    } 

    return true;
  }

  bool VisitCompoundStmt(CompoundStmt *cs) {
    currCompoundStmtNum++;
    string str = to_string(currCompoundStmtNum);

    if (stage == 0) {
      vector<int> tmplist;
      pair <string,vector<int>> tmpfuncCompoundStmt = make_pair (currFunctionName+"_"+str,tmplist); 
      funcCompoundStmtMapVar.insert(tmpfuncCompoundStmt);
    }

    return true;
  }

  bool VisitVarDecl(VarDecl *d) {
    //global variables
    if (stage == 0) {
        if (d->hasGlobalStorage() && !d->isLocalVarDeclOrParm()) {
            varGlobalList.push_back(TheRewriter.getSourceMgr().getSpellingLineNumber(d->getSourceRange().getBegin(), NULL));
        }
        if (d->isLocalVarDeclOrParm()) {
            pair <int,string> tmpVarMapFunc = make_pair (TheRewriter.getSourceMgr().getSpellingLineNumber(d->getSourceRange().getBegin(), NULL),currFunctionName);
            varMapFunc.insert(tmpVarMapFunc);
        }
        if (d->isLocalVarDeclOrParm() && !d->isLocalVarDecl()) {
            functionMapVar[currFunctionName].push_back(TheRewriter.getSourceMgr().getSpellingLineNumber(d->getSourceRange().getBegin(), NULL));
        }
        if (d->isLocalVarDecl()) {
            string str = to_string(currCompoundStmtNum);
            funcCompoundStmtMapVar[currFunctionName+"_"+str].push_back(TheRewriter.getSourceMgr().getSpellingLineNumber(d->getSourceRange().getBegin(), NULL));

            pair <int,string> tmpVarMapFuncCompoundStmt = make_pair (TheRewriter.getSourceMgr().getSpellingLineNumber(d->getSourceRange().getBegin(), NULL),currFunctionName+"_"+str);
            varMapFuncCompoundStmt.insert(tmpVarMapFuncCompoundStmt);
        }
    }

    if (stage == 2) {
        if (TheRewriter.getSourceMgr().getSpellingLineNumber(d->getSourceRange().getBegin(), NULL) == usedtorepVar) {
            usedtorepVarName = d->getQualifiedNameAsString();
            cout<<"usedtorepVarName: "<<usedtorepVarName<<endl;
        }
    }

    return true;
  }

  bool VisitDeclRefExpr(DeclRefExpr *re) {
    if (stage == 1) {
      if(re->getID(*Context)!=position) return true;
      cout<<"mutate here"<<endl;
      cout<<"re-getNameInfo: "<<re->getNameInfo().getAsString()<<endl;
      cout<<"it can use: ";

      vector<int> usedtorepVars;

      int tmpDeclLine = TheRewriter.getSourceMgr().getSpellingLineNumber(re->getDecl()->getSourceRange().getBegin(), NULL);
      if(varMapFunc.count(tmpDeclLine)>0 && varMapFuncCompoundStmt.count(tmpDeclLine)>0){
        // in a func, and in a CompoundStmt

        // can use all the vars in this func
        vector<int> thisFuncMapVars = functionMapVar[varMapFunc[tmpDeclLine]];
        for(int i =0; i<thisFuncMapVars.size(); i++){
            cout<<thisFuncMapVars[i]<<" ";
            usedtorepVars.push_back(thisFuncMapVars[i]);
        }

        // can use all the vars in this CompoundStmt
        vector<int> thisFuncCompoundStmtMapVars = funcCompoundStmtMapVar[varMapFuncCompoundStmt[tmpDeclLine]];
        for(int i =0; i<thisFuncCompoundStmtMapVars.size(); i++){
            cout<<thisFuncCompoundStmtMapVars[i]<<" ";
            usedtorepVars.push_back(thisFuncCompoundStmtMapVars[i]);
        }

        // and can use global vars
        for(int i =0; i<varGlobalList.size(); i++){
            cout<<varGlobalList[i]<<" ";
            usedtorepVars.push_back(varGlobalList[i]);
        }

        cout<<endl;
      } else if (varMapFunc.count(tmpDeclLine)>0 && varMapFuncCompoundStmt.count(tmpDeclLine)==0){
        // in a func, but not in a CompoundStmt

        // func vars
        vector<int> thisFuncMapVars = functionMapVar[varMapFunc[tmpDeclLine]];
        for(int i =0; i<thisFuncMapVars.size(); i++){
            cout<<thisFuncMapVars[i]<<" ";
            usedtorepVars.push_back(thisFuncMapVars[i]);
        }

        // global vars
        for(int i =0; i<varGlobalList.size(); i++){
            cout<<varGlobalList[i]<<" ";
            usedtorepVars.push_back(varGlobalList[i]);
        }

        cout<<endl;
      } else if (varMapFunc.count(tmpDeclLine)==0 && varMapFuncCompoundStmt.count(tmpDeclLine)==0) {
        // in global
        for(int i =0; i<varGlobalList.size(); i++){
            cout<<varGlobalList[i]<<" ";
            usedtorepVars.push_back(varGlobalList[i]);
        }

        cout<<endl;
      } else {
          cout<<"BUG!!! In a compound stmt but not in a func?"<<endl;
      }

      // random select a var to use
      usedtorepVar = usedtorepVars[(rand() % ((usedtorepVars.size()-1)+1))];
      cout<<"it uses: "<<usedtorepVar<<endl;
    }
    
    if (stage == 3) {
      if(re->getID(*Context)!=position) return true;
      cout<<"mutate here"<<endl;
      TheRewriter.ReplaceText(re->getSourceRange().getBegin(), re->getNameInfo().getAsString().size(), usedtorepVarName); 
    }

    return true;
  }

private:
  Rewriter &TheRewriter;
};

// Implementation of the ASTConsumer interface for reading an AST produced
// by the Clang parser.
class MyASTConsumer : public ASTConsumer {
public:
  MyASTConsumer(Rewriter &R) : Visitor(R) {}

  void HandleTranslationUnit(ASTContext &Context) override {
    /* we can use ASTContext to get the TranslationUnitDecl, which is
       a single Decl that collectively represents the entire source file */
    Visitor.Context=&Context;
    stage = 0;
    Visitor.TraverseDecl(Context.getTranslationUnitDecl());
    stage = 1;
    currFunctionName="";
    currCompoundStmtNum=0;
    Visitor.TraverseDecl(Context.getTranslationUnitDecl());
    stage = 2;
    Visitor.TraverseDecl(Context.getTranslationUnitDecl());
    stage = 3;
    Visitor.TraverseDecl(Context.getTranslationUnitDecl());
  }

private:
  MyASTVisitor Visitor;
};

// For each source file provided to the tool, a new FrontendAction is created.
class MyFrontendAction : public ASTFrontendAction {
public:
  MyFrontendAction() {}

  int CopyFile(char *SourceFile,char *NewFile) 
  {  
    ifstream in; 
    ofstream out;  
    in.open(SourceFile,ios::binary);//
    if(in.fail())//
    {     
        cout<<"Error 1: Fail to open the source file."<<endl;    
        in.close();    
        out.close();    
        return 0; 
    }  
    out.open(NewFile,ios::binary);//
    if(out.fail())//
    {     
        cout<<"Error 2: Fail to create the new file."<<endl;    
        out.close();    
        in.close();    
        return 0; 
    }  
    else//
    {     
        out<<in.rdbuf();    
        out.close();    
        in.close();    
        return 1; 
    } 
  }
  
  void EndSourceFileAction() override {
    SourceManager &SM = TheRewriter.getSourceMgr();
    llvm::errs() << "** EndSourceFileAction for: "
                 << SM.getFileEntryForID(SM.getMainFileID())->getName() << "\n";

    CopyFile("main.c", "mainori.c");
    TheRewriter.overwriteChangedFiles();
    rename("main.c", "mainvar.c");
    rename("mainori.c", "main.c");
  }

  std::unique_ptr<ASTConsumer> CreateASTConsumer(CompilerInstance &CI,
                                                 StringRef file) override {
    llvm::errs() << "** Creating AST consumer for: " << file << "\n";
    TheRewriter.setSourceMgr(CI.getSourceManager(), CI.getLangOpts());
    return make_unique<MyASTConsumer>(TheRewriter);
  }

private:
  Rewriter TheRewriter;
};

int main(int argc, const char **argv) {
  srand( (unsigned)time( NULL ) );
  position = atol(argv[3]);

  cout<<"-- running: repVarSameScope-mul"<<endl;
  cout<<"---- position: "<<position<<endl;

  llvm::Expected<clang::tooling::CommonOptionsParser> OptionsParser=CommonOptionsParser::create(argc, argv, VisitAST_Category);
  ClangTool Tool(OptionsParser->getCompilations(), OptionsParser->getSourcePathList());

  Tool.run(newFrontendActionFactory<MyFrontendAction>().get());

  return 0;
}
