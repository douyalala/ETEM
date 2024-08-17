//------------------------------------------------------------------------------
// mutation strategy: replace constant value
// inputs: changed operation
// usage: repIntConstant-mul <path to main.c> --  <changed operation> <position>
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
#include "clang/Lex/LiteralSupport.h"
#include "llvm/ADT/APInt.h"
#include "llvm/ADT/APSInt.h"
#include "llvm/ADT/APFloat.h"
using namespace std;
using namespace llvm;
using namespace clang;
using namespace clang::driver;
using namespace clang::tooling;

static llvm::cl::OptionCategory VisitAST_Category("usage: repIntConstant-mul <path to main.c> --  <changed operation> <position>");
static string newOp = "";
static int64_t position = -1;

class MyASTVisitor : public RecursiveASTVisitor<MyASTVisitor> {
public:
  ASTContext *Context=NULL;
  MyASTVisitor(Rewriter &R) : TheRewriter(R) {}

  bool VisitExpr(Expr *e) {
    if(e->getID(*Context)!=position) return true;
    cout<<"mutate here"<<endl;
      
    IntegerLiteral* il = cast<IntegerLiteral>(e);
    int old_val_int=il->getValue().getSExtValue();
    string newvalue="0";
    if (strcmp(newOp.c_str(),"+1")==0){
      old_val_int++;
      newvalue=to_string(old_val_int);
    } else if (strcmp(newOp.c_str(),"-1")==0){
      old_val_int--;
      newvalue=to_string(old_val_int);
    } else if (strcmp(newOp.c_str(),"*-1")==0){
      old_val_int*=-1;
      newvalue = to_string(old_val_int);
      newvalue = "(" + newvalue + ")";
    } else if (strcmp(newOp.c_str(),"*0")==0){
        newvalue = "0";
    }

    TheRewriter.ReplaceText(il->getSourceRange(), newvalue);
    return false;
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
  newOp = argv[3];
  position = atol(argv[4]);

  cout<<"-- running: repIntConstant-mul"<<endl;
  cout<<"---- newOp: "<<newOp<<endl;
  cout<<"---- position: "<<position<<endl;

  llvm::Expected<clang::tooling::CommonOptionsParser> OptionsParser=CommonOptionsParser::create(argc, argv, VisitAST_Category);
  ClangTool Tool(OptionsParser->getCompilations(), OptionsParser->getSourcePathList());

  Tool.run(newFrontendActionFactory<MyFrontendAction>().get());

  return 0;
}
