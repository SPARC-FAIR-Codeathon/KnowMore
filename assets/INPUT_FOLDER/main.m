function main(InputDataDirectory)
%InputDataDirectory is the file path to a folder that contains:
%   matlab_input.xlsx
%   matlab_data/... directory that contains all data
%
%matlab_input.xlsx contains 1 sheet: "Sheet1" with 2 columns:
%  datasetId:  the unique ID number to the dataset
%  filepath: the path to a .mat file that will be read in
%       Filepath should be something like: 'derviative/FileName.mat. Do not
%       include the parent data folder matlab_data as that is hard-coded in
%       this file
%
%Data must be stored in the directory format:
%   matlab_data/<datasetID>/<filepath>
%e.g.:
%   matlab_data/60/derivative/RatVNMorphology_OutputMetrics.mat
%
%Output: All output will be to the same directory as main.m()
%   1) matlab_output.xlsx will be created and includes:
%       a) Data from each dataset is placed on a sheet named with the datasetID.
%             e.g.: DataSet60
%       b) Combined data from all data sets is placed the sheet AllData
%       c) Data from individual plots that can be created are placed on a
%          sheet named with a code for the independent and dependent
%          variable. Independent & Dependent Variables are defined on
%          AllPlots (see 1d below)
%             e.g., PlotID-3.2
%       d) All possible plot combinations with an explanation of what is
%          plotted is placed on the sheet PlotOptions, which will appear as
%          the very last sheet in the Excel file
%   2) Several PNG figures that plot most variables in the data set against
%      each other. (In future versions, it would be useful to allow the user
%      to define which variables to plot rather than plotting them all.)
%   3) matlab_output.json will contain data organized as:
%         {
%             sheet_name1: {
%                 variable1: [1,2,3,4,5], 
%                 variable2: [1,2,3,4,5], 
%                 variable3: [1,2,3,4,5], 
%                 variable4: [1,2,3,4,5], 
%             }
%             sheet_name2: {
%                 variable1: [1,2,3,4,5], 
%                 variable2: [1,2,3,4,5], 
%                 variable3: [1,2,3,4,5], 
%                 variable4: [1,2,3,4,5], 
%             }
%         }
%
%       a) The .json file can be processed to create plots as well. 
%       b) The variable name in the .json file will match the variable name
%          in the Matlab data files. 
%       c) The sheet name in the .json file will match the sheet name in 
%          the Excel output file. 
%       d) The variable in the first position will *always* be the the
%          independent variable of that parsed data set.
%       e) If the independent variable is categorical, the second variable
%          will be a coded version of the first and the variable name will
%          be the same as the first appended by "_coded".
%       f) The next variable (either 2 or 3) will be the dependent variable
%       g) If a final variable (either 3 or 4) exists, it will be a
%          grouping variable that identifies which dataset the data came
%          from. This is useful for plotting different colors.
%
%Written by: Matthew Schiefer, PhD (1,2,3)
%       for: 2021 SPARC Fair Codeathon
%   Updated: 20 July 2021
%     email: matthew.schiefer@ufl.edu
%
%Affiliations:
% (1): Malcom Randall VA Medical Center, Gainesville, FL
% (2): Department of Biomedical Engineering, University of Florida
% (3): SimNeurix, LLC



%Create an OS-agnostic path to the Excel file that defines the datasets
ExcelInputFile = fullfile(InputDataDirectory, 'matlab_input.xlsx');

%Ensure that InputDataDirectory exists
if ~isdir(InputDataDirectory)
    errordlg([InputDataDirectory ' is not a directory.'],'Invalid Path');
    
%Ensure Excel file exists within the input directory    
elseif ~exist(ExcelInputFile,'file')
    errordlg(['The file matlab-input.xlsx does not exist in ' InputDataDirectory],'Missing File');
    
%Ensure there's a data directory there (don't check to see if the data are there yet)
elseif ~isdir(fullfile(InputDataDirectory,'matlab_data'))
    errordlg([fullfile(InputDataDirectory,'matlab_data') ' is not a directory.'],'Invalid Path');
    
%all good so far, commence with processing    
else
    %Determine which sheets are available in the Excel input file
    [~,SheetsAvailable]=xlsfinfo(ExcelInputFile);
    
    %Ensure Sheet1 is a sheet in the file (should be the only sheet)
    if ~any(contains(SheetsAvailable,'Sheet1'))
        errordlg(['Sheet1 is not a sheet in ' ExcelInputFile],'Missing Sheet');
        
    else
        %Read the data set IDs and filepaths to the data  
        Sheet1=readtable(ExcelInputFile,'Sheet','Sheet1');
        
        %Define the output files
        OutputExcelFile='matlab_output.xlsx';
        OutputJSONFile='matlab_output.json';
        
        %Process each data set
        for TempDataSet=1:size(Sheet1,1)
            %Load the mat file
            MatFile=fullfile(InputDataDirectory,'matlab_data',num2str(Sheet1.datasetId(TempDataSet)), Sheet1.filepath{TempDataSet});
            TempData=load(MatFile);
            
            %Build a table for the variables in this dataset
            CompiledDataTable=CompileData(TempData,Sheet1.filepath{TempDataSet},Sheet1.datasetId(TempDataSet));
            
            %Add this table to the Excel file that was passed in
            writetable(CompiledDataTable,OutputExcelFile,'Sheet',['DataSet' num2str(Sheet1.datasetId(TempDataSet))]);
            
            if TempDataSet==1
                CombinedDataTables=CompiledDataTable;
            else
               %add to the previous data table, but may need to create new variables if the prior table(s) don't contain all variables that were just returned in this table 
               Range=size(CombinedDataTables,1)+[1:size(CompiledDataTable,1)];
               for TempVar=1:length(CompiledDataTable.Properties.VariableNames)
                   CombinedDataTables.([CompiledDataTable.Properties.VariableNames{TempVar}])(Range)=CompiledDataTable.([CompiledDataTable.Properties.VariableNames{TempVar}]);
               end
            end
        end %end for TempDataSet=1:size(Sheet1,1)
        
        %Add this Combined Data Tables (full data set) to the Excel file
        %that was passed in; save on sheet AllData
        writetable(CombinedDataTables,OutputExcelFile,'Sheet','AllData');
        
        %housekeeping
        clear CompiledDataTable Range SheetAvailable TempData TempDataSet TempVar

        %What plots can we create?
        %any column can be the x-axis variable and any column can be the
        %y-axis variable
        %Certain plots we don't want:
            % 1) data (y-axis) versus itself (no information there)
            % 2) data (y-axis) versus dataset name (column 1 of the table)
            % 3) dataset name (col 1) vs dataset ID (col 2)
            % 4) dataset name (col 1) as data (y-axis)
            % 5) dataset ID as data (y-axis)
            % 6) anything non-numeric as data (y-axis)
        PlotOptions=table('size',[nchoosek(9,2)*2,3],'VariableTypes',{'string','string','string'},'VariableNames',{'IndependentVar','DependentVar','PlotID'});
        counter=1;
        for x=3:size(CombinedDataTables,2) %skip columns 1 and 2 for the dataset
            if isnumeric(CombinedDataTables.([CombinedDataTables.Properties.VariableNames{x}]))
                SubplotCounter=1;
                ax=zeros(8,1); %capture axes to create individual figures, too
                for y=2:size(CombinedDataTables,2)
                  
                    if x~=y 
                        PlotOptions.IndependentVar(counter)=CombinedDataTables.Properties.VariableNames{x};
                        PlotOptions.DependentVar(counter)=CombinedDataTables.Properties.VariableNames{y};
                        PlotOptions.PlotID(counter)=['PlotID-' num2str(x) '.' num2str(y)];
                        counter=counter+1;
                        
                        %plot each variable against every other variable as an example
                        figure(x)
                        ax(SubplotCounter)=subplot(2,4,SubplotCounter); %if putting several plots into one figure, should dynamically figure out how many are going to be displayed
                        %if there are a large number of independent
                        %variable values (i.e., it's numeric rather than
                        %categorical), then it would be better to plot this
                        %as a scatter plot rather than a box plot
                        if isnumeric(CombinedDataTables.([CombinedDataTables.Properties.VariableNames{y}])) & ...
                           length(unique(CombinedDataTables.([CombinedDataTables.Properties.VariableNames{y}])))>10
                            ExcelDataTable=table();
                            %when scatter plotting, let's color-code the
                            %datasets by dataset ID
                            UniqueIDs=unique(CombinedDataTables.DataID);
                            for TempID=1:length(UniqueIDs)
                                TempRows=find(CombinedDataTables.DataID==UniqueIDs(TempID));
                                ExcelRows=size(ExcelDataTable,1)+[1:length(TempRows)];
                                ExcelDataTable.([CombinedDataTables.Properties.VariableNames{y}])(ExcelRows)=CombinedDataTables.([CombinedDataTables.Properties.VariableNames{y}])(TempRows);
                                ExcelDataTable.([CombinedDataTables.Properties.VariableNames{x}])(ExcelRows)=CombinedDataTables.([CombinedDataTables.Properties.VariableNames{x}])(TempRows);
                                ExcelDataTable.DataID(ExcelRows)=UniqueIDs(TempID);
                                
                                scatter(CombinedDataTables.([CombinedDataTables.Properties.VariableNames{y}])(TempRows),CombinedDataTables.([CombinedDataTables.Properties.VariableNames{x}])(TempRows),50,'filled')
                                hold on
                            end
                            legend(num2str(UniqueIDs(:)))
                            
                        else
                            %boxplot(CombinedDataTables.([CombinedDataTables.Properties.VariableNames{x}]),CombinedDataTables.([CombinedDataTables.Properties.VariableNames{y}]));
                            ExcelDataTable=table();
                            UniqueIDs=unique(CombinedDataTables.DataID);
                            for TempID=1:length(UniqueIDs)
                                TempRows=find(CombinedDataTables.DataID==UniqueIDs(TempID));
                                if ~isnumeric(CombinedDataTables.([CombinedDataTables.Properties.VariableNames{y}])(TempRows))
                                    [UniqueIndVars,~,UniqueIndVarIndex]=unique(CombinedDataTables.([CombinedDataTables.Properties.VariableNames{y}]));
                                    ExcelRows=size(ExcelDataTable,1)+[1:length(TempRows)];
                                    ExcelDataTable.([CombinedDataTables.Properties.VariableNames{y}])(ExcelRows)=CombinedDataTables.([CombinedDataTables.Properties.VariableNames{y}])(TempRows);
                                    ExcelDataTable.([CombinedDataTables.Properties.VariableNames{y} '_coded'])(ExcelRows)=UniqueIndVarIndex(TempRows);
                                    ExcelDataTable.([CombinedDataTables.Properties.VariableNames{x}])(ExcelRows)=CombinedDataTables.([CombinedDataTables.Properties.VariableNames{x}])(TempRows);
                                    ExcelDataTable.DataID(ExcelRows)=UniqueIDs(TempID);
                                    scatter(UniqueIndVarIndex(TempRows),CombinedDataTables.([CombinedDataTables.Properties.VariableNames{x}])(TempRows),50,'filled');
                                    if iscell(UniqueIndVars)
                                        set(gca,'XTick',[1:length(UniqueIndVars)],'XTickLabels',UniqueIndVars);
                                    else
                                        set(gca,'XTick',[1:length(UniqueIndVars)],'XTickLabels',{UniqueIndVars});
                                    end
                                    xlim([.5 length(UniqueIndVars)+0.5])
                                else
                                    ExcelRows=size(ExcelDataTable,1)+[1:length(TempRows)];
                                    ExcelDataTable.([CombinedDataTables.Properties.VariableNames{y}])(ExcelRows)=CombinedDataTables.([CombinedDataTables.Properties.VariableNames{y}])(TempRows);
                                    ExcelDataTable.([CombinedDataTables.Properties.VariableNames{x}])(ExcelRows)=CombinedDataTables.([CombinedDataTables.Properties.VariableNames{x}])(TempRows);
                                    scatter(CombinedDataTables.([CombinedDataTables.Properties.VariableNames{y}])(TempRows),CombinedDataTables.([CombinedDataTables.Properties.VariableNames{x}])(TempRows),50,'filled')
                                end
                                hold on
                            end
                            legend(num2str(UniqueIDs(:)),'location','best')
                        end
                        LabelText=CombinedDataTables.Properties.VariableNames{y};
                        LabelText(strfind(LabelText,'_'))=' ';
                        xlabel(LabelText);
                        LabelText=CombinedDataTables.Properties.VariableNames{x};
                        LabelText(strfind(LabelText,'_'))=' ';
                        ylabel(LabelText);
                        box on
                        title(PlotOptions.PlotID{counter-1});
                        set(gca,'fontsize',16,'fontweight','bold')
                        xtickangle(90);
                        
                        %write data to Excel
                        writetable(ExcelDataTable,OutputExcelFile,'Sheet',PlotOptions.PlotID{counter-1});
                        %also write to JSON file
                        writeJSON(PlotOptions.PlotID{counter-1},ExcelDataTable,OutputJSONFile)
                        
                        SubplotCounter=SubplotCounter+1;
                    end
                end
                set(gcf,'units','normalized','position',[0 0 1 1]);
                saveas(gcf,['Plots-' num2str(x) '.x.png']);
                saveas(gcf,['Plots-' num2str(x) '.x.svg']);
                    for subfig=1:8
                        if ax(subfig)>0
                        figure(100+subfig)
                        ax2=axes;
                        copyobj(get(ax(subfig),'Children'),ax2);
                        set(gca,'Xlabel',get(ax(subfig),'Xlabel'),'Ylabel',get(ax(subfig),'Ylabel'),'Title',get(ax(subfig),'Title'),'XTick',get(ax(subfig),'XTick'),'XTickLabel',get(ax(subfig),'XTickLabel'),'XLim',get(ax(subfig),'XLim'),'YLim',get(ax(subfig),'YLim'),'fontsize',16,'fontweight','bold')
                        legend(get(ax(subfig),'Legend').String,'location','best')
                        box on
                        xtickangle(90);
                        %set(gcf,'units','normalized','position',[0 0 1 1]);
                        saveas(gcf,['Plots-' get(ax(subfig)).Title.String '.png']);
                        saveas(gcf,['Plots-' get(ax(subfig)).Title.String '.svg']);
                        close(100+subfig);
                        end
                    end
                if ishandle(x)
                    close(x);
                end
            end
        end
        
        %Write these plotting sets to a sheet. Ideally this would become
        %interactive so that the user could specific which plot(s) to
        %actually show
        writetable(PlotOptions,OutputExcelFile,'Sheet','PlotOptions');
        
        %close JSON sheet
        writeJSON([],[],OutputJSONFile)
    end %end if ~any(contains(SheetsAvailable,'Sheet1'))
end %end ~strcmpi(ExcelInputFile(end-4:end),'.xlsx')


end %end function




function CompiledDataTable=CompileData(TempData,DataFile,DataID)
%Compile data actually takes the data in the TempData structure and
%processes it into a table. BUT SEE THE NEXT NOTE!

%======================================================================
%NOTE:
%I'm going to have to do a little housekeeping here. Unfortunately, the
%datasets we're testing from studies 60, 64, and 65 are all identical and
%contain the data from all 3 datasets. Certainly we don't want triplicates.
%So, I'm going to delete out rows that contain the wrong information for
%that study. Specifically:
% Study 60 pertains to rats, with subject sample (sub_sam) strings that
%           start with "R"
% Study 64 pertains to pigs, with sub_sam starting with "P"
% Study 65 pertains to humans, with sub_sam starting with "C"
%If the data sets are every updated so that datasets don't contain the same
%data, the if statements a few lines down can be removed.
%======================================================================

%TempData is a structure that must only contain cell arrays. Each cell is
%the data for a subject or sample and can contain a string or a vector
CompiledDataTable=table('size',[0 0]); %empty table
VarNames=fieldnames(TempData);

%We're going to assume that the cell array variable with the largest size
%contains the total number of observations. Ideally, NumObservations would
%be a protected variable within the dataset, but, alas, that would make
%things easy.
NumObservations=zeros(size(VarNames));
for i=1:size(VarNames,1)
    if iscell(TempData.([VarNames{i}]))
        NumObservations(i)=length(TempData.([VarNames{i}]));
    end
end

%Everything should have the same number of observations. But something has
%a different number, we're going to be forced to ignore it
VarNames(~ismember(NumObservations,max(NumObservations)))=[];
NumObservations=max(NumObservations);

if NumObservations==0
    error(['Could not determine the number of observations within the data file ' Sheet1.filepath{TempDataSet}],'Unable to compile data');
else
    StartRow=0;
    for i=1:NumObservations
        AddRow=0;
        if isfield(TempData,'sub_sam') %this likely only exists in Datasets 60, 64, and 65
            %see NOTE above
            if (DataID==60) & (strcmpi(TempData.sub_sam{i}(1),'R')) | ...
               (DataID==64) & (strcmpi(TempData.sub_sam{i}(1),'P')) | ...
               (DataID==65) & (strcmpi(TempData.sub_sam{i}(1),'C'))
                AddRow=1;
            end %end if (DataID == 60) & ...
        else
            AddRow=0; %Change this to a 1 to work with (or attempt to work with) ANY mat file. This is not a good idea until the datasets are standardized, but it can be used for testing purposes.
        end %end if isfield(TempData,'sub_sam')
        
        if AddRow==1
            %if the cell array used contains a count in each cell, then I need
            %to know the value in the cell. If, instead, it contains a vector
            %in the cell, then I need to know the length
            if all(cellfun(@length,(TempData.([VarNames{1}])))) %base the count on whatever is in the first position of the variable list
                %working with counts
                Observations=TempData.([VarNames{1}]){i};
            else
                %working with vectors
                Observations=length(TempData.([VarNames{1}]){i});
            end
            
            %determine the rows in the table to write to
            Range=StartRow+[1:Observations];
            
            %add data to the table
            CompiledDataTable.DataFile(Range)=repmat({DataFile},length(Range),1);
            CompiledDataTable.DataID(Range)=DataID;
            for TempVar=1:length(VarNames)
                if ischar(TempData.([VarNames{TempVar}]){i})
                    if length(TempData.([VarNames{TempVar}]){i})>1
                        %string with 2 or more characters
                        CompiledDataTable.([VarNames{TempVar}])(Range)=repmat({TempData.([VarNames{TempVar}]){i}},length(Range),1);
                    else
                        %single character string, no repmat needed
                        CompiledDataTable.([VarNames{TempVar}])(Range)=TempData.([VarNames{TempVar}]){i};
                    end
                else
                    %numeric, presumably
                    CompiledDataTable.([VarNames{TempVar}])(Range)=TempData.([VarNames{TempVar}]){i};
                end
            end
            StartRow=size(CompiledDataTable,1);
            
        end %end if AddRow==1
    end %end for i=1:NumObservations
end %end if NumObservations==0

end

function writeJSON(SheetName,DataTable,JSONFile)
%This function will write the data into a JSON file. Subsequent calls will
%append to the file if it already exists. Passing empty fields will close
%the file: writeJSON([],[],JSONFile);

if ~exist(JSONFile,'file')
    %create file and open
    fid=fopen(JSONFile,'w');
    fprintf(fid,'{\n'); %opening brace
else
    fid=fopen(JSONFile,'a');
end

if ~isempty(SheetName)
    fprintf(fid,'\t"%s": {\n',SheetName);
    for TempVar=1:size(DataTable,2)
        fprintf(fid,'\t\t"%s": [',DataTable.Properties.VariableNames{TempVar});
        if isnumeric(DataTable.([DataTable.Properties.VariableNames{TempVar}]))
            fprintf(fid,'%g,',DataTable.([DataTable.Properties.VariableNames{TempVar}])(1:end-1));
            fprintf(fid,'%g],\n',DataTable.([DataTable.Properties.VariableNames{TempVar}])(end));
        else
            
            if iscell(DataTable.([DataTable.Properties.VariableNames{TempVar}]))
                %cell array of string
                DataCellString=cellfun(@(x) ['"' regexprep(x,',',' ') '",'],DataTable.sub_sam,'UniformOutput',false); %remove any commas from the string and add a comma to the end of the text in each cell
                DataCellString=cell2mat(DataCellString');
                fprintf(fid,'%s',DataCellString(1:end-1));
            else
                %string
                DataString=[repmat('"',size(DataTable,1),1), DataTable.([DataTable.Properties.VariableNames{TempVar}]),repmat('",',size(DataTable,1),1) ]';
                DataString=DataString(:);
                fprintf(fid,'%s',DataString(1:end-1));
            end
            fprintf(fid,'],\n');
        end
    end
    fprintf(fid,'\t},\n');
else
    fprintf(fid,'}');
end

fclose(fid);

end